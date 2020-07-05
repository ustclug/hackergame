import base64

import OpenSSL
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from backend.user.models import User, Term


class RegisterSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField()

    class Meta:
        model = User
        fields = ['username', 'password', 'password_confirm']
        extra_kwargs = {'password': {'write_only': True}}

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise ValidationError("Passwords are not same.")
        return data

    def create(self, validated_data):
        private_key = OpenSSL.crypto.load_privatekey(
            OpenSSL.crypto.FILETYPE_PEM, settings.PRIVATE_KEY)
        user = User(
            email=validated_data['email'],
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        pk = str(user.pk)
        sig = base64.b64encode(OpenSSL.crypto.sign(
            private_key, pk.encode(), 'sha256')).decode()
        user.token = pk + ':' + sig
        user.save()
        return user


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = '__all__'
