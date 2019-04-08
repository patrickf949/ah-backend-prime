import os
from django.conf import settings
from django.contrib.auth import authenticate
from authors.apps.authentication.models import User

def register_user(email, username):
    '''This Function registers users using their social media information and returns their credentials'''
    already_user = User.objects.filter(email=email)
    password = settings.SOCIAL_PASSWORD
    if not email:
        return 'Empty email address'
    if not already_user.exists():
        user = {
            'username': username,
            'email': email,
            'password':password
        }
        new_user = User.objects.create_user(**user)
        new_user.is_active
        new_user.save()
        return {
            'email': new_user.email,
            'username': new_user.username,
            'token': new_user.token
        }
    else:
        return 'This email address already exists! Please log in!'
