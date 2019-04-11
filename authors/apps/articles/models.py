from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.template.defaultfilters import slugify
from django.utils import timezone
from authors.apps.profiles.models import Profile
from authors.apps.authentication.models import User
from django.contrib.postgres import fields
from django.contrib.contenttypes.fields import GenericRelation


class LikeDislikeManager(models.Manager):
    '''Model Manager responsible for returning the likes/dislikes'''

    def likes(self):
        '''We take the queryset with records greater than 0'''
        return self.get_queryset().filter(vote__gt=0)

    def dislikes(self):
        '''We take the queryset with records less than 0'''
        return self.get_queryset().filter(vote__lt=0)



class LikeDislike(models.Model):
    '''Model to effeciently handle likes-dislikes with other models'''
    LIKE = 1
    DISLIKE = -1

    VOTES = (
        (DISLIKE, 'Dislike'),
        (LIKE, 'Like')
    )

    vote = models.SmallIntegerField(choices=VOTES)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    objects = LikeDislikeManager()

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
    tagsList = models.ManyToManyField(
        'Tag',
        related_name='articles'
    )
    author = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='author'
    )
    votes = GenericRelation(LikeDislike, related_query_name='articles')

    class Meta:
        get_latest_by = ['id']


    @staticmethod
    def get_slug(title):
        '''Method returns the slag of an article'''
        try:
            id = Articles.objects.latest().id
            return slugify(title + "-" + str(hex(id)))
        except Articles.DoesNotExist:
            return slugify(title + "-alpha")

    @property
    def average_rating(self):
        ratings = self.articlerating_set.all()\
            .aggregate(ratings=models.Avg("ratings"))
        if not ratings['ratings']:
            return 0
        return float('%.1f' % ratings['ratings'])

    @property
    def comments(self):
        return self.comment_set.all()

    def __str__(self):
        return self.title

class Tag(models.Model):
    tag = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.tag

class ArticleRating(models.Model):
    """
    model for rating  article
    """
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)
    article = models.ForeignKey(Articles, on_delete=models.CASCADE)
    ratings = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class Comment(models.Model):
    """
    Model for comments
    """
    body = models.TextField()
    parentId = models.IntegerField()
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    author = models.ForeignKey(
        Profile, 
        on_delete=models.CASCADE,      
    )
    article = models.ForeignKey(
        Articles, 
        on_delete=models.CASCADE, 
    )
    class Meta:
        get_latest_by = ['createdAt']


    @property
    def reply(self):
        return self.reply_set.all()

    def __str__(self):
        return self.body

