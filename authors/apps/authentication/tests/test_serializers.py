from .base import BaseTest
from unittest.mock import patch, MagicMock, PropertyMock
from authors.apps.authentication.serializers import (
    LoginSerializer, UserSerializer)
from rest_framework.serializers import ValidationError
from django.test import TestCase


class TestLoginSerializer(TestCase):
    """
    class handling test on user models/serializers

    """

    def test_email_not_in_validate_function(self):
        """
        method to test if email is not provided in the validate function in serializers
        """
        empty_email = {
            "email": None,
            "password": "password@123"
        }
        with self.assertRaises(ValidationError) as error:
            LoginSerializer().validate(empty_email)
        self.assertEqual(
            error.exception.args[0],
            'An email address is required to log in.')

    def test_password_not_in_validate_function(self):
        """
        method to test if password is not provided in the validate function in serializers
        """
        empty_password = {
            "email": "anyatibrian@glo.com",
            "password": None
        }
        with self.assertRaises(ValidationError) as error:
            LoginSerializer().validate(empty_password)
        self.assertEqual(
            error.exception.args[0],
            'A password is required to log in.')

    def test_update_user(self):
        """
        method to test the update of the user data
        """

        class UpdateUser:

            def save(self):
                pass

            def set_password(self, password):
                pass

        update_data = {
            "email": "supreme@andela.com",
            "password": "Prime@supreme",
            "username": "fudgesupreme"
        }

        update_instance = UpdateUser()
        self.assertEqual(
            UserSerializer().update(
                update_instance,
                update_data),
            update_instance)
