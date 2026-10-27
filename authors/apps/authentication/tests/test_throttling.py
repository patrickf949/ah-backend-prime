from unittest.mock import patch
from django.core.cache import cache
from rest_framework import status
from rest_framework.throttling import ScopedRateThrottle, SimpleRateThrottle
from .base import BaseTest


class ThrottlingTestCase(BaseTest):
    """Verifies API rate limiters and throttling enforcement."""

    def test_auth_rate_limiting_enforced(self):
        """Hitting auth endpoints beyond the rate limit returns 429."""
        cache.clear()
        throttle_rates = {
            'anon': None,
            'user': None,
            'auth': '2/min',
            'uploads': None,
        }
        with patch.dict(SimpleRateThrottle.THROTTLE_RATES, throttle_rates):
            # First request
            r1 = self.client.post(self.login_url, data={'user': {'email': 'a@b.com', 'password': 'WrongPassword123'}}, format='json')
            self.assertEqual(r1.status_code, status.HTTP_400_BAD_REQUEST)

            # Second request
            r2 = self.client.post(self.login_url, data={'user': {'email': 'a@b.com', 'password': 'WrongPassword123'}}, format='json')
            self.assertEqual(r2.status_code, status.HTTP_400_BAD_REQUEST)

            # Third request within same minute should be throttled
            r3 = self.client.post(self.login_url, data={'user': {'email': 'a@b.com', 'password': 'WrongPassword123'}}, format='json')
            self.assertEqual(r3.status_code, status.HTTP_429_TOO_MANY_REQUESTS)

