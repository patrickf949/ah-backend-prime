VALID_USER_DATA = {
    "user": {
        "username": "anyatijude",
        "email": "anyatibrian@glo.com",
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

ERROR_LOGIN={
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