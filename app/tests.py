from unittest import TestCase
from django.http import HttpRequest
from django.contrib.auth import get_user_model
from unittest.mock import Mock
from .views import login
from django.urls import reverse

# Custom User model
User = get_user_model()

class LoginTestCase(TestCase):
    def test_login(self):
        # Set up test environment and data
        request = Mock()
        request.build_absolute_uri.return_value = 'http://example.com/callback'
        oauth = Mock()
        oauth.auth0.authorize_redirect.return_value = '/dashboard'

        # Call the code to be tested
        response = login(request)

        # Assert that the code is behaving as expected
        self.assertEqual(response, '/dashboard')
        oauth.auth0.authorize_params.assert_called_with({})
        request.build_absolute_uri.assert_called_with(reverse('callback'))
        oauth.auth0.authorize_redirect.assert_called_with(request, 'http://example.com/callback')
