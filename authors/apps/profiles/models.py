from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from authors.apps.authentication.models import User

class Profile(models.Model):
    """
    class creating a data model to hold information about users
    that is used to create the user profile
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    full_name = models.CharField(max_length=255, blank=True)
    image = models.URLField(blank=True)
    follows = models.ManyToManyField(
        'self',
        related_name='followed_by',
        symmetrical=False
    )


    def __str__(self):
        return self.user.username

    def follow(self, profile):
        """Follow profile if we're not already following profile."""
        self.follows.add(profile)

    def unfollow(self, profile):
        """Unfollow profile if we're already following profile."""
        self.follows.remove(profile)

    def is_following(self, profile):
        """Returns True if we're following `profile`; False otherwise."""
        return self.follows.filter(pk=profile.pk).exists()

    def is_followed_by(self, profile):
        """Returns True if profile is following us; False otherwise."""
        return self.followed_by.filter(pk=profile.pk).exists()


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    signals the profile model when a user has been registered
    for their profile to be created
       """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()
