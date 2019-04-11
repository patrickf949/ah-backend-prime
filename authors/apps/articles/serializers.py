from rest_framework import serializers
from . import models
from authors.apps.profiles.serializers import ProfileSerializer


class TagsRelationSerializer(serializers.RelatedField):
    def get_queryset(self):
        return models.Tag.objects.all()

    def to_representation(self, value):
        return value.tag


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Tag
        fields = ('tag', 'created_at')

    def to_representation(self, instance):
        return instance.tag



class ArticleSerializer(serializers.ModelSerializer):
    author = ProfileSerializer(required=False)
    average_rating = serializers.SerializerMethodField()
    tagList = TagsRelationSerializer(many=True, required=False, source='tagsList')
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()

    class Meta:
        fields = (
            'author',
            'title',
            'average_rating',
            'description',
            'body',
            'createdAt',
            'updatedAt',
            'slug',
            'tagList',
            'likes',
            'dislikes'
        )
        model = models.Articles
        read_only_fields = ['author', 'slug']

    def get_average_rating(self, obj):
        return obj.average_rating
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['tagList'] = TagSerializer(instance.tagsList,
                                                  many=True).data
        return representation

    def get_likes(self, instance):
        '''Serializer method to return the number of likes of an article'''
        return instance.votes.likes().count()

    def get_dislikes(self, instance):
        '''Serializer method to return the number of dislikes of an article'''
        return instance.votes.dislikes().count()


    def create(self, validated_data):
        tags = self.initial_data['tags']
        article = models.Articles.objects.create(**validated_data)

        if not isinstance(tags, list):
            raise serializers.ValidationError("Tags must be in a list")

        for tag in tags:
            tag_name = tag.lower()
            query_tag = models.Tag.objects.filter(tag=tag_name)
            if not query_tag.exists():
                article.tagsList.create(tag=tag_name)
            else:
                article.tagsList.add(query_tag[0].id)
        
        return article
    def get_comments(self, obj):
        return obj.comment.__all__

class CommentSerializer(serializers.ModelSerializer):
    """
    Serializer for comment to an article
    """
    author = ProfileSerializer(required=False)
    article = ArticleSerializer(required=False)

    class Meta:
        fields = '__all__'
        model = models.Comment
        read_only_fields = ['article', 'author', 'parentId']
    
    def get_replies(self, obj):
        return obj.reply.__all__


class RateArticleSerializer(serializers.ModelSerializer):
    """
    rating serializer class
    """
    tagList = TagsRelationSerializer(many=True, required=False, source='tagsList')

    class Meta:
        model = models.ArticleRating
        fields = ('id', 'user', 'article', 'ratings', 'created_at', 'tagList')
        read_only_fields = ['id', 'created_at']

    def validate_ratings(self, value):
        if value < 0 or value > 5:
            raise serializers.ValidationError(
                            'Ratings should be numbers between 0-5')
        return value
