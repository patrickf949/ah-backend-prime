import re
from rest_framework import serializers

def validate_registration(data):
    '''Function to validate user input from user registration'''
    username = data.get("username", None)
    email = data.get("email", None)
    password = data.get("password", None)

    if not username or len(username.strip()) == 0:
        raise serializers.ValidationError(
            {
                'username': 'Username should not be left empty'
            }
        )
    elif len(username) < 4:
        raise serializers.ValidationError(
            {
                'username': 'Username should not be less than 4 characters'
            }
        )
    elif ' ' in username:
        raise serializers.ValidationError(
            {
                'username': 'Username should not contain any spaces'
            }
        )

    if not email or len(email.strip()) == 0:
        raise serializers.ValidationError(
            {
                'email': 'Email should not be left empty'
            }
        )
    elif not re.search(r'[^@]+@[^@]+\.[^@]+', email):
        raise serializers.ValidationError(
            {
                'email': 'Invalid email address'
            }
        )
    elif ' ' in email:
        raise serializers.ValidationError(
            {
                'email': 'Email should not contain any spaces'
            }
        )

    if not password or len(password.strip()) == 0:
        raise serializers.ValidationError(
            {
                'password': 'Please provide the password'
            }
        )
    elif len(str(password)) < 8 or len(str(password)) > 20:
        raise serializers.ValidationError(
            {
                'password': 'Password length should not be less than 8 characters or greater than 20 characters'
            }
        )
    elif not re.search("[A-Z]", password)\
            or not re.search("[0-9]", password)\
            or not re.search("[a-z]", password)\
            or not re.search(r"[~\!@#\$%\^&\*\(\)_\+{}\":;,<>+'\[\]]", password):
        raise serializers.ValidationError(
            {
                'password': 'Password should have atleast one lowercase character,one Uppercase character, one Integer and one Special character'
            }
        )
    elif ' ' in password:
        raise serializers.ValidationError(
            {
                'password': 'Password should not contain any spaces'
            }
        )
