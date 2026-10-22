from unittest.mock import patch
import datetime
import jwt
from django.conf import settings
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.test import APITestCase

from authors.apps.authentication.models import User, UserPassword
from authors.apps.authentication.serializers import LoginSerializer, PasswordResetSerializser


class AuthenticationCoverageGapTest(APITestCase):
    """Covers missing lines in authentication models, serializers, and views."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='authgapuser', email='authgap@example.com', password='password123'
        )

    def test_create_user_validations(self):
        with self.assertRaises(TypeError):
            User.objects.create_user(username=None, email='valid@example.com', password='123')
        with self.assertRaises(TypeError):
            User.objects.create_user(username='validname', email=None, password='123')

    @override_settings(PASSWORD_HASHERS=[
        'django.contrib.auth.hashers.MD5PasswordHasher',
        'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    ])
    def test_user_password_methods(self):
        user = self.user
        self.assertEqual(user.get_full_name, user.username)
        self.assertEqual(user.get_short_name(), user.username)

        # Usable password checks
        self.assertTrue(user.has_usable_password())
        auth_hash = user.get_session_auth_hash()
        self.assertTrue(len(auth_hash) > 0)

        # Set unusable password
        user.set_unusable_password()
        self.assertFalse(user.has_usable_password())

        # Usable password checks on pending and unsaved user
        unsaved = User(username='unsaved', email='unsaved@example.com')
        self.assertFalse(unsaved.has_usable_password())
        unsaved.set_password('temp')
        self.assertTrue(unsaved.has_usable_password())
        unsaved.set_unusable_password()
        self.assertFalse(unsaved.has_usable_password())

        # Set unusable password on saved user
        user.set_unusable_password()
        self.assertFalse(user.has_usable_password())
        self.assertFalse(user.check_password('anything'))

        # Set password on saved user
        user.set_password('newcustompassword')
        self.assertTrue(user.check_password('newcustompassword'))

        # When raw_password is None
        self.assertFalse(user.check_password(None))

        # Rehash when hasher is not preferred
        from django.contrib.auth.hashers import make_password
        p_hash = make_password('rehashpass', hasher='pbkdf2_sha256')
        UserPassword.objects.filter(user=user).update(password_hash=p_hash)
        user.refresh_from_db()
        self.assertTrue(user.check_password('rehashpass'))

        # When credential does not exist
        UserPassword.objects.filter(user=user).delete()
        user.refresh_from_db()
        self.assertFalse(user.check_password('anything'))
        self.assertFalse(user.has_usable_password())
        empty_auth_hash = user.get_session_auth_hash()
        self.assertTrue(len(empty_auth_hash) > 0)

        # Credential str
        cred = UserPassword.objects.create(user=user, password_hash='mockhash')
        self.assertIn('credential for', str(cred))

    @patch('authors.apps.authentication.serializers.authenticate')
    def test_login_deactivated_user(self, mock_auth):
        self.user.is_active = False
        mock_auth.return_value = self.user
        serializer = LoginSerializer(data={
            'email': self.user.email,
            'password': 'password123'
        })
        with self.assertRaises(ValidationError) as ctx:
            serializer.is_valid(raise_exception=True)
        self.assertIn('This user has been deactivated.', str(ctx.exception))

    def test_reset_password_serializer_none_password(self):
        serializer = PasswordResetSerializser()
        with self.assertRaises(ValidationError):
            serializer.validate_password(None)

    def test_user_retrieve_update_view(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('users')
        response = self.client.put(url, {'user': {'bio': 'updated bio'}}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_password_reset_expired_token(self):
        expired_payload = {
            'id': self.user.id,
            'exp': datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=1)
        }
        expired_token = jwt.encode(expired_payload, settings.SECRET_KEY, algorithm='HS256')
        url = reverse('password-reset', kwargs={'token': expired_token})
        response = self.client.put(url, {'user': {'password': 'newpass', 'confirmpassword': 'newpass'}}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data.get('error'), 'token expired')
