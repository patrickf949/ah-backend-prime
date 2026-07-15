from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.template.defaultfilters import slugify
from django.utils import timezone
from authors.apps.profiles.models import Profile
from authors.apps.authentication.models import User
from django.contrib.postgres import fields
from django.contrib.contenttypes.fields import GenericRelation
from authors.settings import WORD_LENGTH, WORD_PER_MINUTE


class ReactionManager(models.Manager):
    """Manager exposing common reaction querysets and aggregates"""

    def likes(self):
        return self.get_queryset().filter(reaction=Reaction.LIKE)

    def dislikes(self):
        return self.get_queryset().filter(reaction=Reaction.DISLIKE)

    def summary(self):
        """Return a {reaction: count} mapping for reactions present"""
        return {
            row['reaction']: row['total']
            for row in self.get_queryset()
            .values('reaction')
            .annotate(total=models.Count('id'))
            .order_by('-total')
        }


class Reaction(models.Model):
    """A user's emoji reaction to any content object (article, comment)"""
    LIKE = 'like'
    DISLIKE = 'dislike'
    LOVE = 'love'
    CLAP = 'clap'
    LAUGH = 'laugh'
    WOW = 'wow'
    SAD = 'sad'
    FIRE = 'fire'
    INSIGHTFUL = 'insightful'

    REACTION_CHOICES = (
        (LIKE, '👍'),
        (DISLIKE, '👎'),
        (LOVE, '❤️'),
        (CLAP, '👏'),
        (LAUGH, '😂'),
        (WOW, '😮'),
        (SAD, '😢'),
        (FIRE, '🔥'),
        (INSIGHTFUL, '💡'),
    )

    # Reactions that replace each other when a user switches between them
    OPPOSITES = {LIKE: DISLIKE, DISLIKE: LIKE}

    reaction = models.CharField(max_length=20, choices=REACTION_CHOICES)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reactions')
    created_at = models.DateTimeField(auto_now_add=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    objects = ReactionManager()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'content_type', 'object_id', 'reaction'],
                name='unique_user_object_reaction'
            )
        ]
        indexes = [
            models.Index(fields=['content_type', 'object_id']),
        ]

    @classmethod
    def emoji_for(cls, reaction):
        return dict(cls.REACTION_CHOICES).get(reaction, '')

    def __str__(self):
        return '{} {}'.format(self.reaction, self.emoji_for(self.reaction))


class Articles(models.Model):
    """
    Create model for Article storage
    """
    title = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    body = models.TextField()
    createdAt = models.DateTimeField(auto_now_add=True)
    updatedAt = models.DateTimeField(auto_now=True)
    slug = models.SlugField(max_length=220)
    image = models.CharField(max_length=300, blank=True)
    tagsList = models.ManyToManyField(
        'Tag',
        related_name='articles'
    )
    author = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name='author'
    )
    reactions = GenericRelation(Reaction, related_query_name='articles')

    class Meta:
        get_latest_by = ['id']

    @staticmethod
    def get_slug(title):
        """Method returns the slag of an article"""
        try:
            id = Articles.objects.latest().id
            return slugify(title + "-" + str(hex(id)))
        except Articles.DoesNotExist:
            return slugify(title + "-alpha")

    @property
    def average_rating(self):
        ratings = self.articlerating_set.all() \
            .aggregate(ratings=models.Avg("ratings"))
        if not ratings['ratings']:
            return 0
        return float('%.1f' % ratings['ratings'])

    @property
    def favorite_count(self):
        favorites = FavoriteArticle.objects.filter(article=self).count()
        if not favorites:
            return 0
        return favorites

    def __str__(self):
        return self.title

    @property
    def reading_time(self):
        """ method estimating the reading time of an article
        by counting words
        params:
            - count: number of words in text, initialised to 0
            - result: time it takes a user to read the text
        """
        count = 0
        count += len(self.body) / WORD_LENGTH
        result = int(count / WORD_PER_MINUTE)
        if result >= 1:
            reading_time = str(result) + " minute read"
        else:
            reading_time = " less than a minute read"
        return reading_time


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

    def __str__(self):
        return '{}'.format(self.ratings)


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
    commentHistory = models.TextField(default="")
    reactions = GenericRelation(Reaction, related_query_name='comments')

    class Meta:
        get_latest_by = ['createdAt']

    def __str__(self):
        return self.body


class ReportArticle(models.Model):
    """
    class handling reporting of articles functionality
    """
    reporter = models.ForeignKey('profiles.Profile', on_delete=models.CASCADE)
    article = models.ForeignKey('articles.Articles', on_delete=models.CASCADE)
    reported_at = models.DateTimeField(auto_now_add=True)
    violation = models.CharField(max_length=300)

    def __str__(self):
        return self.violation

    class Meta:
        ordering = ['-reported_at']


class FavoriteArticle(models.Model):
    """
    Model for favoriting
    """

    is_favorite = models.BooleanField(default=False)
    favorited_by = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE
    )
    article = models.ForeignKey(
        Articles,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return str(self.pk)
