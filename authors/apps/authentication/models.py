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
        return self.generated_jwt_token

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
        return token.decode('utf-8')

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
                message="Welcome to Author's Haven." + \
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
        activate_url = get_current_site(current_url).domain + url
        email_subject = "Author haven password reset"
        email_message = 'hi {} please follow the link ' \
                        'below to reset  your account\n'.format(self.username) + activate_url
        send_mail(subject=email_subject,
                  message=email_message,
                  recipient_list=[self.email, ],
                  fail_silently=False,
                  from_email=EMAIL_HOST_USER
                  )
        return True
