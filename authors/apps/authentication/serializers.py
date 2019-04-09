from django.contrib.auth import authenticate
from rest_framework import serializers

from authors.apps.authentication.models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """Serializers registration requests and creates a new user."""

    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'password', 'token']

        extrakwargs = {
            'id': {
                'read_only': True
            }
        }

    def create(self, validated_data):
        """
        Use the `create_user` method we wrote earlier to create a new user.
        """
        return User.objects.create_user(**validated_data)


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(max_length=255)
    username = serializers.CharField(max_length=255, read_only=True)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)

    def validate(self, data):

        email = data.get('email', None)
        password = data.get('password', None)

        if email is None:
            raise serializers.ValidationError(
                'An email address is required to log in.'
            )

        if password is None:
            raise serializers.ValidationError(
                'A password is required to log in.'
            )

        user = authenticate(username=email, password=password)
        if user is None:
            raise serializers.ValidationError(
                'A user with this email and password was not found.'
            )

        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        return {
            'email': user.email,
            'username': user.username,
            'token': user.token
        }


class UserSerializer(serializers.ModelSerializer):
    """Handles serialization and deserialization of User objects."""

    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'token')
        read_only_fields = ('token',)

    def update(self, instance, validated_data):
        """Performs an update on a User."""

        password = validated_data.pop('password', None)

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        if password is not None:
            instance.set_password(password)

        instance.save()

        return instance


class PasswordResetSerializser(serializers.ModelSerializer):
    password = serializers.CharField(
        required=True, min_length=8, write_only=True)
    confirmpassword = serializers.CharField(
        required=True, min_length=8, write_only=True)

    class Meta:
        model = User
        fields = ('password', 'confirmpassword')

    def validate_password(self, value):
        if value is None:
            raise serializers.ValidationError(
                'please enter your password here'
            )
        return value


class PasswordResetResquestSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email',)
