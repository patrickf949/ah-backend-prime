from django.db import models
from django.template.defaultfilters import slugify
from django.utils import timezone
from authors.apps.profiles.models import Profile

class Articles(models.Model):
    """
    Create models for Article storage
    """

    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    body = models.TextField()
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=220)
    author = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE, 
        related_name='author'
    )

    class Meta:
        get_latest_by = ['id']
    
    def get_slug(title):
        try:
            id = Articles.objects.latest().id
            return slugify(title + "-" + str(hex(id)))
        except Articles.DoesNotExist:
            return slugify(title + "-alpha")

    def __str__(self):
        return self.title


