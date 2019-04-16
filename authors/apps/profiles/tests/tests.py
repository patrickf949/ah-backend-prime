import json
from .test_base import BaseTestProfile
from rest_framework import status
from django.urls import reverse
from authors.apps.profiles.renderers import ProfileJSONRenderer
from authors.apps.profiles.tests.test_data import (VALID_LOGIN_DATA,
                                                   VALID_USER_DATA,
                                                   UPDATE_DATA,
                                                   VALID_USER_DATA_2,
                                                   VALID_LOGIN_DATA_2)


class TestUserProfile(BaseTestProfile):

    def test_get_profiles(self):
        """
        test if user can return the profile of all users if current user is
        authenticated
        """
        response = self.client.get(
            self.profile_url,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' +
            self.user_token)
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)
        self.assertEqual('anyatijude',
                         response.data[0]['username'])

    def test_get_profiles_not_allowed(self):
        """
        test if user cannot return the profile of all users if current user is not
        authenticated
        """
        response = self.client.get(self.profile_url,
                                   content_type='application/json')
        self.assertEqual(response.status_code,
                         status.HTTP_403_FORBIDDEN)
        self.assertIn(
            'Authentication credentials were not provided.', str(
                response.data))

    def test_edit_profile(self):
        """
        test if a user can edit his profile
        """
        url = reverse('update-profile', kwargs={'username': 'anyatijude'})
        response = self.client.put(
            url,
            content_type='application/json',
            data=json.dumps(UPDATE_DATA),
            HTTP_AUTHORIZATION='Bearer ' +
            self.user_token)
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)
        self.assertIn('Profile Updated successfully',
                      str(response.data))

    def test_get_single_profile(self):
        """
        test if an authenticated user can get his profile
        """
        url = reverse('get-profile', kwargs={'username': 'anyatijude'})
        response = self.client.get(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' +
            self.user_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('profile', str(response.data))

    def test_edit_not_allowed(self):
        """
        test that a user cannot edit profile another person's profile
        """
        response = self.client.post(
            self.register_url,
            content_type='application/json',
            data=json.dumps(VALID_USER_DATA_2))
        self.activate_email = reverse('activate-user',
                                      kwargs={'token': response.data['token']}
                                      )
        self.client.get(
            self.activate_email
        )
        login_response_2 = self.client.post(self.login_url,
                                            content_type='application/json',
                                            data=json.dumps(VALID_LOGIN_DATA_2)
                                            )
        user_token = login_response_2.data['token']
        url = reverse('update-profile',
                      kwargs={'username': 'anyatijude'}
                      )
        response = self.client.put(url,
                                   content_type='application/json',
                                   data=json.dumps(UPDATE_DATA),
                                   HTTP_AUTHORIZATION='Bearer ' + user_token
                                   )
        self.assertEqual(response.status_code,
                         status.HTTP_403_FORBIDDEN)
        self.assertIn('You do not have privileges to edit this profile',
                      str(response.data))

    def test_create_profile(self):
        """
        test if a user profile is created
        """
        response = self.client.post(
            self.register_url,
            content_type='application/json',
            data=json.dumps(VALID_USER_DATA_2))
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_json_renderer(self):
        self.assertEquals(isinstance
                        (ProfileJSONRenderer().render({"data": "test"}), 
                        dict), False)

    def test_get_users_list(self):
        """
        test if a list of all users and their profiles is returned
        """
        response = self.client.get(
            self.user_list_url,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' +
            self.user_token)
        self.assertEqual(response.status_code,
                         status.HTTP_200_OK)

    def test_unauthorised_get_users_list(self):
        """
        test if an unauthorised user cannot get the users list
        """
        response = self.client.get(
            self.user_list_url,
            content_type='application/json'
                                    )
        self.assertEqual(response.status_code,
                         status.HTTP_403_FORBIDDEN)

    def test_follow_user(self):
        '''Test for following a user'''
        response = self.client.post(
            self.register_url,
            content_type='application/json',
            data=json.dumps(VALID_USER_DATA_2)
        )
        self.activate_email = reverse(
            'activate-user',
            kwargs={'token': response.data['token']}
        )
        self.client.get(
            self.activate_email
        )
        login_response_2 = self.client.post(
            self.login_url,
            content_type='application/json',
            data=json.dumps(VALID_LOGIN_DATA_2)
        )
        user_token = login_response_2.data['token']

        url = reverse(
            'follow-profile',
            kwargs={'username': 'anyatijude'}
        )

        response = self.client.post(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' + user_token
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_201_CREATED
        )
        self.assertEqual(response.data['message'], 'You are now following anyatijude')

    def test_unfollow_user(self):
        '''Test for unfollowing a user'''
        response = self.client.post(
            self.register_url,
            content_type='application/json',
            data=json.dumps(VALID_USER_DATA_2)
        )
        self.activate_email = reverse(
            'activate-user',
            kwargs={'token': response.data['token']}
        )
        self.client.get(
            self.activate_email
        )
        login_response_2 = self.client.post(
            self.login_url,
            content_type='application/json',
            data=json.dumps(VALID_LOGIN_DATA_2)
        )
        user_token = login_response_2.data['token']

        url = reverse(
            'follow-profile',
            kwargs={'username': 'anyatijude'}
        )

        self.client.post(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' + user_token
        )

        response = self.client.delete(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' + user_token
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_200_OK
        )
        self.assertEqual(response.data['message'], 'You have unfollowed anyatijude')

    def test_follow_non_existant_user(self):
        '''Test for following non-existant user'''
        url = reverse(
            'follow-profile',
            kwargs={'username': 'Ogwal'}
        )
        response = self.client.post(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' +
            self.user_token
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )
        self.assertEqual(response.data['detail'], 'A profile with this username was not found.')

    def test_unfollow_non_existant_user(self):
        '''Test for unfollowing non-existant user'''
        url = reverse(
            'follow-profile',
            kwargs={'username': 'Ogwal'}
        )
        response = self.client.delete(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' +
            self.user_token
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_404_NOT_FOUND
        )
        self.assertEqual(response.data['detail'], 'A profile with this username was not found.')

    def test_follow_oneself(self):
        '''Test for one following themselves'''
        url = reverse(
            'follow-profile',
            kwargs={'username': 'anyatijude'}
        )
        response = self.client.post(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' +
            self.user_token
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(response.data['errors'][0], 'You can not follow yourself.')

    def test_follow_user_again(self):
        '''Test for following a user once again'''
        response = self.client.post(
            self.register_url,
            content_type='application/json',
            data=json.dumps(VALID_USER_DATA_2))
        self.activate_email = reverse(
            'activate-user',
            kwargs={'token': response.data['token']}
        )
        self.client.get(
            self.activate_email
        )
        login_response_2 = self.client.post(
            self.login_url,
            content_type='application/json',
            data=json.dumps(VALID_LOGIN_DATA_2)
        )
        user_token = login_response_2.data['token']

        url = reverse(
            'follow-profile',
            kwargs={'username': 'anyatijude'}
        )

        self.client.post(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' + user_token
        )

        response = self.client.post(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' + user_token
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(response.data['errors'][0], 'You already follow this user')


    def test_unfollow_already_unfollowed_user(self):
        '''Test for unfollowing an unfollowed user'''
        response = self.client.post(
            self.register_url,
            content_type='application/json',
            data=json.dumps(VALID_USER_DATA_2))
        self.activate_email = reverse(
            'activate-user',
            kwargs={'token': response.data['token']}
        )
        self.client.get(
            self.activate_email
        )
        login_response_2 = self.client.post(
            self.login_url,
            content_type='application/json',
            data=json.dumps(VALID_LOGIN_DATA_2)
        )
        user_token = login_response_2.data['token']

        url = reverse(
            'follow-profile',
            kwargs={'username': 'anyatijude'}
        )

        self.client.delete(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' + user_token
        )

        response = self.client.delete(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' + user_token
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(response.data['errors'][0], 'You do not follow anyatijude')

    def test_unfollowing_myself(self):
        url = reverse(
            'follow-profile',
            kwargs={'username': 'anyatijude'}
        )
        response = self.client.delete(
            url,
            content_type='application/json',
            HTTP_AUTHORIZATION='Bearer ' +
            self.user_token
        )
        self.assertEqual(
            response.status_code,
            status.HTTP_400_BAD_REQUEST
        )
        self.assertEqual(response.data['errors'][0], 'You can not unfollow yourself.')
