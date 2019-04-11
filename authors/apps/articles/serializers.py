from rest_framework import serializers
from . import models
from authors.apps.profiles.serializers import ProfileSerializer


class ArticleSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(required=False)
    average_rating = serializers.SerializerMethodField()

    class Meta:
        fields = '__all__'
        model = models.Articles
        read_only_fields = ['author', 'slug']

    def get_average_rating(self, obj):
        return obj.average_rating


class RateArticleSerializer(serializers.ModelSerializer):
    """
    rating serializer class
    """
    class Meta:
        model = models.ArticleRating
        fields = ('id', 'user', 'article', 'ratings', 'created_at')
        read_only_fields = ['id', 'created_at']

    def validate_ratings(self, value):
        if value < 0 or value > 5:
            raise serializers.ValidationError(
                            'Ratings should be numbers between 0-5')
        return value
