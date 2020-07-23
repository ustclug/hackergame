from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from user.models import User, Term


class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        try:
            validate_password(validated_data['password'])
        except DjangoValidationError as e:
            raise ValidationError({'password': list(e)[0]})
        return User.objects.create_user(username=validated_data['username'],
                                        password=validated_data['password'])


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = '__all__'


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    allow_terms = serializers.BooleanField(required=False)


class ProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='last_name')

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'token', 'name', 'date_joined']


class ProfileUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='last_name')

    class Meta:
        model = User
        fields = ['name']


class PublicProfileSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='last_name')

    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'name']
