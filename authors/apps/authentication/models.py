import os
import jwt
from authors.settings import EMAIL_HOST_USER, SECRET_KEY
from django.db.models.signals import post_save
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.urls import reverse
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.contrib.auth.hashers import check_password as verify_hash
from django.contrib.auth.hashers import make_password
from django.utils.crypto import salted_hmac
from django.db import models


class UserManager(BaseUserManager):
    """
    Django requires that custom users define their own Manager class. By
    inheriting from `BaseUserManager`, we get a lot of the same code used by
    Django to create a `User` for free.

    All we have to do is override the `create_user` function which we will use
    to create `User` objects. on
    """

    def create_user(self, username, email, password=None):
        """Create and return a `User` with an email, username and password."""
        if username is None:
            raise TypeError('Users must have a username.')

        if email is None:
            raise TypeError('Users must have an email address.')

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user

    def create_superuser(self, username, email, password):
        """
      Create and return a `User` with superuser powers.

      Superuser powers means that this use is an admin that can do anything
      they want.
      """
        if password is None:
            raise TypeError('Superusers must have a password.')
        user = self.create_user(username, email, password)
        user.is_superuser = True
        user.is_staff = True
        user.is_active = True
        user.save()

        return user


class User(AbstractBaseUser, PermissionsMixin):
    # Password hashes live in the user_passwords table (UserPassword), which
    # only has rows for accounts registered with email + password. Social
    # sign-in accounts have no credential row at all, so there is no shared
    # or fake password to leak.
    password = None

    _pending_password_hash = None
    _password_pending = False

    username = models.CharField(
        db_index=True,
        max_length=255,
        unique=True
    )

    email = models.EmailField(
        db_index=True,
        unique=True
    )

    is_active = models.BooleanField(default=False)

    is_staff = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def __str__(self):
        """
        Returns a string representation of this `User`.

        This string is used when a `User` is printed in the console.
        """
        return self.email

    def set_password(self, raw_password):
        """Stage a hash for the user_passwords row; None removes it."""
        self._pending_password_hash = (
            make_password(raw_password) if raw_password is not None else None
        )
        self._password_pending = True
        if self.pk:
            self._store_password()

    def set_unusable_password(self):
        self.set_password(None)

    def _store_password(self):
        if not self._password_pending:
            return
        if self._pending_password_hash is None:
            UserPassword.objects.filter(user=self).delete()
        else:
            UserPassword.objects.update_or_create(
                user=self,
                defaults={'password_hash': self._pending_password_hash}
            )
        self._password_pending = False

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self._store_password()

    def check_password(self, raw_password):
        if raw_password is None:
            return False
        try:
            credential = self.credential
        except UserPassword.DoesNotExist:
            return False

        def setter(raw):
            # rehash transparently when Django's preferred algorithm changes
            self.set_password(raw)

        return verify_hash(raw_password, credential.password_hash, setter)

    def has_usable_password(self):
        if self._password_pending:
            return self._pending_password_hash is not None
        if not self.pk:
            return False
        return UserPassword.objects.filter(user=self).exists()

    def get_session_auth_hash(self):
        """Session hash for admin logins, keyed on the credential row."""
        try:
            hash_value = self.credential.password_hash
        except UserPassword.DoesNotExist:
            hash_value = ''
        key_salt = 'authors.apps.authentication.models.User.get_session_auth_hash'
        return salted_hmac(key_salt, hash_value, algorithm='sha256').hexdigest()

    @property
    def is_social(self):
        """Derived, not stored: a user is 'social' iff they hold at least
        one linked social identity."""
        return self.social_accounts.exists()

    @property
    def get_full_name(self):
        """
      This method is required by Django for things like handling emails.
      Typically, this would be the user's first and last name. Since we do
      not store the user's real name, we return their username instead.
      """
        return self.username

    def get_short_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically, this would be the user's first and last name. Since we do
        not store the user's real name, we return their username instead.
        """
        return self.username

    @property
    def token(self):
        """
        method sets token as a dynamic property allowing us to get a user's
        token by calling user.token instead of calling the user.generated_jwt_token()
        """
        return self.generated_jwt_token()

    def generated_jwt_token(self):
        """
        This method generates a JWT token that stores a user

        """
        exp_time = datetime.now() + timedelta(hours=3)
        token = jwt.encode({
            'id': self.pk,
            'email': self.email,
            'exp': int(exp_time.strftime('%s'))
        }, SECRET_KEY, algorithm='HS256')
        return token

    @staticmethod
    def call_back(link):
        def fun(sender, instance, **kwargs):
            token = instance.generated_jwt_token()
            url = reverse('activate-user', kwargs={
                'token': token
            })

            domain = str(link) + str(url)
            send_mail(
                subject=instance.username + " Welcome to Author's Haven",
                message="Welcome to Author's Haven." +
                        "\nLogin using this link\nhttp://" + domain,
                from_email=EMAIL_HOST_USER,
                recipient_list=[instance.email],
                fail_silently=False)

        return fun

    @staticmethod
    def get_url(url):
        """
        Get the current url
        """
        post_save.connect(User.call_back(url), sender=User, weak=False)

    def send_password_reset_link(self, current_url, token):
        """
        method that sends mail to the user
        """
        url = reverse('password-reset', args=[token])
        print("token", url)
        activate_url = current_url.META.get('HTTP_ORIGIN', get_current_site(current_url).domain)+"/"+token+"/passwordreset"
        #activate_url = (get_current_site(current_url).domain + url)
        email_subject = "Author haven password reset"
        email_message = 'hi {} please follow the link ' \
                        'below to reset  your account\n'.format(
                            self.username) + activate_url
        send_mail(subject=email_subject,
                  message=email_message,
                  recipient_list=[self.email, ],
                  fail_silently=False,
                  from_email=EMAIL_HOST_USER
                  )
        return True


class UserPassword(models.Model):
    """Credential row for accounts registered with email + password.

    Social sign-in accounts intentionally have no row here — the absence of
    a credential is what makes them passwordless, so there is no shared
    secret that could be leaked and replayed against the login endpoint.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='credential'
    )
    password_hash = models.CharField(max_length=128)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_passwords'

    def __str__(self):
        return 'credential for {}'.format(self.user.email)
