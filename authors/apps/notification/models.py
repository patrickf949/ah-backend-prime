from authors.settings import EMAIL_HOST_USER
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse
from django.core.mail import send_mail
from authors.apps.profiles.models import Profile
from authors.apps.articles.models import Articles,Comment,FavoriteArticle


class NotificationSetting(models.Model):
    """
    class for hoping in and out of notifications
    """
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    email_notifications = models.BooleanField(default=True)
    in_app_notifications = models.BooleanField(default=True)

    def __str__(self):
        return "notification setting"


class Notification(models.Model):
    """
    the Notification models
    """
    receiver = models.ForeignKey(Profile, models.CASCADE, related_name='receive_notification')
    message = models.CharField(max_length=100, null=True)
    link = models.CharField(max_length=255, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return '{}'.format(self.message)

    class Meta:
        ordering = ['created_at', ]

    @staticmethod
    def send_email_notification(instance, args, message):
        """
        method that sends email notification to the users
        """
        subject = "you have new notification from  from authors haven "
        recipient = []
        for i in args:
            recipient.append(i.user.email)
        send_mail(subject=subject,
                  from_email=EMAIL_HOST_USER,
                  message=message,
                  recipient_list=recipient,
                  fail_silently=False
                  )


@receiver(post_save, sender=Articles)
def notify_users_articles_created(sender, instance, created, **kwargs):
    profile = Profile.objects.filter(follows=instance.author.pk)
    link = reverse('articles')
    message = "{} posted {}".format(instance.author.user.username, instance.title)
    for user in profile:
        settings = NotificationSetting.objects.filter(user=user).first()
        if settings.email_notifications and settings.in_app_notifications:
            Notification.objects.create(
                receiver=user,
                message=message,
                link='http://127.0.0.1:8000{}'.format(link),
                is_read=False,
            )
            Notification.send_email_notification(instance, profile, message)


@receiver(post_save, sender=Profile)
def create_notifications_setting(sender, instance, created, **kwargs):
    """
    signals the configures user email setting for notifications
    """
    if created:
        NotificationSetting.objects.create(user=instance)


@receiver(post_save, sender=Comment)
def notify_user_when_favorite_articles_comments(sender, instance, created, **kwargs):
    if created:
        fovarited = FavoriteArticle.objects.filter(favorited_by=instance.author.pk)
        recipients = []
        message = "{} comment on {}\n with \n {}".format(
                    instance.author.user.username,
                    instance.article.title,
                    instance.body
                )
        for user in fovarited:
            settings = NotificationSetting.objects.filter(user=user.favorited_by).first()
            if settings.email_notifications and settings.in_app_notifications:
                Notification.objects.create(
                    receiver=user.favorited_by,
                    message=message,
                    is_read=False,
                )
                Notification.send_email_notification(instance, [user.favorited_by,], message)



