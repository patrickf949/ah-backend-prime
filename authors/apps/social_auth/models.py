from django.db import models


class SocialAccount(models.Model):
    """A linked social identity for a user.

    The (provider, provider_user_id) pair is the identity key for social
    login — no passwords are involved anywhere in the social flow. One user
    may hold several rows (e.g. signed in with both Google and Facebook).
    """
    GOOGLE = 'google'
    FACEBOOK = 'facebook'
    TWITTER = 'twitter'
    PROVIDER_CHOICES = (
        (GOOGLE, 'Google'),
        (FACEBOOK, 'Facebook'),
        (TWITTER, 'Twitter'),
    )

    user = models.ForeignKey(
        'authentication.User',
        on_delete=models.CASCADE,
        related_name='social_accounts'
    )
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    provider_user_id = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'social_accounts'
        constraints = [
            models.UniqueConstraint(
                fields=['provider', 'provider_user_id'],
                name='unique_provider_identity'
            )
        ]

    def __str__(self):
        return '{}:{} -> {}'.format(
            self.provider, self.provider_user_id, self.user.email
        )
