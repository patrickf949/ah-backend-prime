from .base import BaseTest
from rest_framework import status
from .test_data import ( 
                         valid_login_data, 
                         valid_user_data, 
                         login_response,
                         empty_login_email, 
                         empty_login_password
                         )


class LoginUserTest(BaseTest):
    """
    test userlogin with correct credentials

    """
    def test_user_login(self):
        self.client.post(
            self.register_url,
            data=valid_user_data,
            format='json'
        )
        self.response= self.client.post(
            self.login_url,
            data=valid_login_data,
            format='json'
        )
        self.assertEquals(self.response.status_code , 
        status.HTTP_200_OK)
        self.assertEquals(self.response.data,
        login_response)
    
    def test_invalide_user_login(self):
        """
         test user login with invalide credentials

        """
        self.response= self.client.post(
            self.login_url,
            data=valid_login_data,
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
            data=empty_login_email,
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
            data=empty_login_password,
            format='json'
        )
        self.assertEquals(self.response.status_code , 
        status.HTTP_400_BAD_REQUEST)
        self.assertEquals(self.response.data['errors']['password'][0], "This field may not be blank."
        )

    
