from .base import BaseTest
from rest_framework import status
from .test_data import ( 
                         VALID_LOGIN_DATA, 
                         VALID_USER_DATA, 
                         LOGIN_RESPONSE,
                         EMPTY_LOGIN_EMAIL, 
                         EMPTY_LOGIN_PASSWORD
                         )


class LoginUserTest(BaseTest):
    """
    test userlogin with correct credentials

    """
    def test_user_login(self):
        self.client.post(
            self.register_url,
            data=VALID_USER_DATA,
            format='json'
        )
        self.response= self.client.post(
            self.login_url,
            data=VALID_LOGIN_DATA,
            format='json'
        )
        self.assertEquals(self.response.status_code , 
        status.HTTP_200_OK)
        self.assertEquals(self.response.data,
        LOGIN_RESPONSE)
    
    def test_invalide_user_login(self):
        """
         test user login with invalide credentials

        """
        self.response= self.client.post(
            self.login_url,
            data=VALID_LOGIN_DATA,
            format='json'
        )
        self.assertEquals(self.response.status_code , 
        status.HTTP_400_BAD_REQUEST)
        self.assertEquals(self.response.data['errors']['error'][0], "A user with this email and password was not found."
        )
    
    def test_empty_login(self):
        """ 
        test user login without email

        """
        self.response= self.client.post(
            self.login_url,
            data=EMPTY_LOGIN_EMAIL,
            format='json'
        )
        self.assertEquals(self.response.status_code , 
        status.HTTP_400_BAD_REQUEST)
        self.assertEquals(self.response.data['errors']['email'][0], "This field may not be blank."
        )
    
    def test_empty_password(self):
        """
        test user login without password

        """
        self.response= self.client.post(
            self.login_url,
            data=EMPTY_LOGIN_PASSWORD,
            format='json'
        )
        self.assertEquals(self.response.status_code , 
        status.HTTP_400_BAD_REQUEST)
        self.assertEquals(self.response.data['errors']['password'][0], "This field may not be blank."
        )

    
