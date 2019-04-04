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

    def __str__(self):
        return self.user.username


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
