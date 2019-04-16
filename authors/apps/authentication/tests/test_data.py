VALID_USER_DATA = {
    "user": {
        "username": "anyatijude",
        "email": "anyatibrian@glo.com",
        "password": "Password@123"
    }
}
VALID_USER_DATA_2 = {
    "user": {
        "username": "fitzokou",
        "email": "fitz@gmail.com",
        "password": "Password@123"
    }
}

EMPTY_USERNAME = {
    "user": {
        "username": "",
        "email": "anyatijude@glo.com",
        "password": "Password@123"
    }
}

INVALID_USERNAME = {
    "user": {
        "username": "fds",
        "email": "anyatijude@glo.com",
        "password": "Password@123"
    }
}

EMPTY_EMAIL = {
    "user": {
        "username": "anyatijude",
        "email": "",
        "password": "Password@123"
    }
}

EMPTY_SPACE_USERNAME = {
    "user": {
        "username": "anyatijude ",
        "email": "anyatijude@glo.com",
        "password": " "
    }
}

EMPTY_SPACE_EMAIL = {
    "user": {
        "username": "anyatijude",
        "email": "anyatijude@glo.com ",
        "password": " "
    }
}

EMPTY_PASSWORD = {
    "user": {
        "username": "anyatijude",
        "email": "anyatijude@glo.com",
        "password": " "
    }
}

PASSWORD_WITH_SPACE = {
    "user": {
        "username": "anyatijude",
        "email": "anyatijude@glo.com",
        "password": "Aaaa2!jcdjc "
    }
}


INVALID_PASSWORD = {
    "user": {
        "username": "anyatijude",
        "email": "anyatijude@glo.com",
        "password": "password"
    }
}

SHORT_PASSWORD = {
    "user": {
        "username": "anyatijude",
        "email": "anyatijude@glo.com",
        "password": "pass"
    }
}

INVALID_EMAIL = {
    "user": {
        "username": "anyatijude",
        "email": "anyatij",
        "password": "Password@123"
    }
}
VALID_LOGIN_DATA = {
    "user": {
        "email": "anyatibrian@glo.com",
        "password": "Password@123"
    }
}
LOGIN_RESPONSE = {'email': 'anyatijude@glo.com', 'username': 'anyatijude'}

EMPTY_LOGIN_EMAIL = {
    "user": {
        "email": "",
        "password": "Password@123"
    }
}

EMPTY_LOGIN_PASSWORD = {
    "user": {
        "email": "anyatibrian@glo.com",
        "password": ""
    }
}

ERROR_LOGIN ={
    "errors": {
        "error": [
            "A user with this email and password was not found."
        ]
    }
}

EMAIL_ACTIVATION_DATA = {
    "email": "anyatibrian@glo.com"
}

PASSWORD_RESET_DATA = {
    "password":"password@123",
    "confirmpassword":"password@123"
}
NO_SOCIAL_EMAIL_DATA = {
    'username': 'testname',
    'id': 'skdvnskjvcn'
}

VALID_SOCIAL_DATA = {
    'username': "testname",
    'email': "test@email.com",
    'id': "skdvnskjvcn"
}

EMPTY_SOCIAL_EMAIL_DATA = {
    'username': 'testname',
    'email': "",
    'id': 'skdvnskjvcn'
}

INVALID_GOOGLE_TOKEN = {
    'user_token': {
        'auth_token': 'jY291bnRzLmdvb2dsZS5jb20iLCJhenAiOiI0MDc0MDg3MTgxOTIuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJhdWQiOiI0MDc0MDg3MTgxOTIuYXBwcy5nb29nbGV1c2VyY29udGVudC5jb20iLCJzdWIiOiIxMTc1ODkzNjkwNzMwNDYwNzI1OTciLCJlbWFpbCI6ImNhcnRwaXhAZ21haWwuY29tIiwiZW1haWxfdmVyaWZpZWQiOnRydWUsImF0X2hhc2giOiJkRDQ2VXl1a2t5SUF1UDgwZjV4SF9BIiwibmFtZSI6Iktpc2Vra2EgRGF2aWQiLCJwaWN0dXJlIjoiaHR0cHM6Ly9saDMuZ29vZ2xldXNlcmNvbnRlbnQuY29tLy16cWRkYlRTZUp4WS9BQUFBQUFBQUFBSS9BQUFBQUFBQUNEMC9lWklFOFRoTnRmQS9zOTYtYy9waG90by5qcGciLCJnaXZlbl9uYW1lIjoiS2lzZWtrYSIsImZhbWlseV9uYW1lIjoiRGF2aWQiLCJsb2NhbGUiOiJlbiIsImlhdCI6MTU1NDM3MzU1MCwiZXhwIjoxNTU0Mzc3MTUwfQ.QdhDxFYVxkgJONWOCNkqm9ZQsFSltQL-ljF5BCNplUi8lg_v6b7C9ow2kT7BIBFrBLH3e5h5EU9OabYPheR1jCwac3NHH1LsyyvqJC02BMHDuEzxpNmjmrvqc_xR_BRf-5h6PgznL9wYGLi1d7lt5T-oB5Thepd6j5olnqFX7wDb6h3enrWf9o-'
    }
}

INVALID_TWITTER_TOKENS = {
    'user_token': {
        'auth_token': '6lkZAkasGRkyTRecXuv0mXQofiUuNsYBRZAZC2ZB8wgZ AkasGRkyTRecXuv0mXQofiUuNsYBRZAZC2ZB8wgZDZD'
    }
}

INVALID_FACEBOOK_TOKEN = {
    'user_token': {
        'auth_token': 'EAAKiNAKiHTIBAKoAcmZBQycSlFK7XqIYGFzOOXgfFw2oTZBJbeGoIVF12X7FWzgEQP8fK4dF5X6U2tLvwJLeZBL5yR90503NyZBOf1i09cAf2dihWN28QxVpx2xj8ycQBw5NwdqmZCeZBAPZACkDE5RM1SutYYlnIwLAyJxcdPl0Y3xtfnWfRwfEZAfPFDN4UyEUIlCOcZADq1gZDZD'
    }
}
