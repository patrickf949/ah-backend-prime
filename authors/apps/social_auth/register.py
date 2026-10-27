from authors.apps.authentication.models import User
from authors.apps.social_auth.models import SocialAccount


def _unique_username(base):
    """Derive a username that does not collide with an existing account."""
    username = base or 'user'
    candidate = username
    suffix = 1
    while User.objects.filter(username=candidate).exists():
        suffix += 1
        candidate = '{}{}'.format(username, suffix)
    return candidate


def register_social_user(provider, provider_user_id, email, username, full_name='', image=''):
    '''Log in (or register) a user identified by a social provider.

    Identity is the (provider, provider_user_id) pair — no passwords are
    created or checked anywhere in this flow. A social login against an
    email that already has a regular account links the identity to that
    account: both prove control of the same verified email.
    '''
    if not email:
        return 'Empty email address'

    account = SocialAccount.objects.filter(
        provider=provider,
        provider_user_id=str(provider_user_id)
    ).select_related('user').first()

    if account is not None:
        user = account.user
    else:
        user = User.objects.filter(email=email).first()
        if user is None:
            user = User.objects.create_user(
                username=_unique_username(username),
                email=email
            )
            user.is_active = True
            user.save()
        SocialAccount.objects.create(
            user=user,
            provider=provider,
            provider_user_id=str(provider_user_id)
        )

    # Sync profile info (full_name, image) brought over from social profile
    profile = getattr(user, 'profile', None)
    if profile is not None:
        updated = False
        if full_name and not profile.full_name:
            profile.full_name = full_name
            updated = True
        if image and not profile.image:
            profile.image = image
            updated = True
        if updated:
            profile.save()

    return {
        'email': user.email,
        'username': user.username,
        'token': user.token
    }
