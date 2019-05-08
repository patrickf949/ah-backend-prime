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
            'password': password
        }
        new_user = User.objects.create_user(**user)
        new_user.is_active = True
        new_user.save()
        new_user = authenticate(username=email, password=password)
        data = {
            "email": new_user.email,
            "username": new_user.username,
            "token": new_user.token
        }
        return data
    else:
        try:
            registered_user = authenticate(email=email, password=password)
            return {
                'email': registered_user.email,
                'username': registered_user.username,
                'token': registered_user.token,
            }
        except:
            return "Kindly log In using the application."
