from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from group.models import Group, Application


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        exclude = ['users']


class GroupApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = '__all__'
