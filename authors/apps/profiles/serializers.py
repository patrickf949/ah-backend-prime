from rest_framework import serializers
from .models import Profile


class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', required=False)
    email = serializers.CharField(source='user.email', required=False)
    bio = serializers.CharField(allow_blank=True, required=False)
    followers_no = serializers.SerializerMethodField()
    following_no = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = ('username',
                  'bio',
                  'email',
                  'full_name',
                  'image',
                  'followers_no',
                  'following_no'
                  )
        read_only_fields = ('username', )

    def check_request(self):
        '''Function to check the validity and authenticity of a request'''
        request = self.context.get('request')

        if request is None:
            return False

        if not request.user.is_authenticated:
            return False


    def get_followers_no(self, instance):
        '''Method calculates the number of users a user follows'''

        self.check_request()

        followee = instance

        return Profile.follows.through.objects.filter(to_profile_id=followee.pk).count()

    def get_following_no(self, instance):
        '''Method calculates the number of users following a user'''

        self.check_request()

        followee = instance

        return Profile.followed_by.through.objects.filter(from_profile_id=followee.pk).count()
