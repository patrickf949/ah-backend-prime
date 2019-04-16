from authors.apps.authentication.models import User, UserManager
from django.test import TestCase
from unittest.mock import patch, MagicMock, PropertyMock
from .base import BaseTest


class TestModel(TestCase):

    def test_empty_email(self):
        User.objects.create_user(username="anyatibrian",
                                 email="",
                                 password="password@123"
                                 )
        self.assertTrue('Users must have an email address.')

    def test_password_given_on_creating_super_user(self):
        """
        Method test if password is provided when registering a superuser
        """

        class MockCreateUser:
            is_superuser = False
            is_staff = False

            @classmethod
            def __call__(cls, *args, **kwargs):
                return cls()

            def save(self):
                pass

        with patch('authors.apps.authentication.models.UserManager.create_user',
        new_callable=MockCreateUser):
            user = UserManager().create_superuser(
                username='anyatibrian',
                email='anyatibrian@gmail.com',
                password='password@123')
            self.assertTrue(user.is_superuser)
            self.assertTrue(user.is_staff)
            self.assertEqual(user.save(), None)

    def test_missing_password_on_creating_superuser(self):
        """
        Method to test if the password is missing when creating the user
        """
        with self.assertRaises(TypeError):
            UserManager().create_superuser(
                username="anyatibrian",
                email="anyatibrian@gmail.com",
                password=None)

    def test_string_data_returned(self):
        """
        Method to test if the data returned in the models is a string
        """
        self.response = User.objects.create_user(
            username="anyatibrian",
            email="anyatibrian@gmail.com",
            password="fudgeSupreme")
        self.assertEqual(self.response.__str__(), 'anyatibrian@gmail.com')
