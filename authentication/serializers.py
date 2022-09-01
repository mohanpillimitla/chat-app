from django.contrib.auth import authenticate
from django.db import transaction
from django.db.models import Q
from rest_framework import serializers
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from .models import User
from rest_framework.permissions import IsAdminUser,IsAuthenticated


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=False)
    username = serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    confirm_password = serializers.CharField(write_only=True, required=True)
    token = serializers.SerializerMethodField(method_name='get_token')

    class Meta:
        model = User
        fields = ('username', 'password',
                  'confirm_password', 'email',
                  'token',
                  )
        extra_kwargs = {
            'username': {'required': True}
        }

    @staticmethod
    def get_token(obj):
        return Token.objects.get(user=obj).key

    def validate(self, attrs):
        if attrs['password'] != attrs['confirm_password']:
            raise serializers.ValidationError(
                {"password": 'PASSWORD_NOT_MATCHED'})
        return attrs

    def create(self, validated_data):
        with transaction.atomic():
            user = User.objects.create(
                username=validated_data['username'],
                is_active=True,
                email=validated_data['email']
            )
            user.set_password(validated_data['password'])
            user.save()
            token, created = Token.objects.get_or_create(user=user)
            return user
            
    def update(self,instance,validated_data):
        for key,value in validated_data.items():
            instance[key] = value
        instance.save()
        return instance



    @staticmethod
    def get_user_id(obj):
        return obj.id


class LoginSerializer(serializers.Serializer):
    login_id = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    token = serializers.CharField(max_length=255, read_only=True)
    username = serializers.SerializerMethodField()

    def validate(self, data):
        username = data.get("login_id", None)
        filters = Q(username__iexact=username)
        password = data.get("password", None)
        try:
            user = User.objects.get(filters)
        except User.MultipleObjectsReturned:
            raise serializers.ValidationError(
                'NO_USER_FOUND'
            )
        except User.DoesNotExist:
            raise serializers.ValidationError(
                'NO_USER_FOUND'
            )
        else:
            if not user.check_password(password):
                user = None
        if user is None:
            raise serializers.ValidationError(
                'NO_USER_FOUND'
            )
        token, created = Token.objects.get_or_create(user=user)

        return {
            'login_id': user.username,
            'email': user.email,
            'token': token.key,
            'username': user.username
        }

    def get_username(self, obj):
        return obj.get('username')

    def get_user_id(self, obj):
        return obj.get('user_id')

    def get_email(self, obj):
        return obj.get('email')


class ChangePasswordSerializer(serializers.Serializer):
    """
        serializer for password change
    """

    old_password = serializers.CharField(required=True)
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password])
    re_password = serializers.CharField(required=True, write_only=True)

    def validate(self, attrs):
        if attrs['password'] != attrs['re_password']:
            raise serializers.ValidationError(
                'PASSWORD_NOT_MATCHED'
            )
        return attrs
