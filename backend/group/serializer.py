from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueTogetherValidator

from group.models import Group, Application
from user.serializer import PublicProfileSerializer


class RuleSerializer(serializers.ModelSerializer):
    has_phone_number = serializers.BooleanField(source='rule_has_phone_number')
    has_email = serializers.BooleanField(source='rule_has_email')
    has_name = serializers.BooleanField(source='rule_has_name')
    must_be_verified_by_admin = serializers.BooleanField(source='rule_must_be_verified_by_admin')
    email_suffix = serializers.CharField(source='rule_email_suffix', allow_null=True,
                                         max_length=50, required=False)

    class Meta:
        model = Group
        fields = [
            'has_phone_number',
            'has_email',
            'has_name',
            'must_be_verified_by_admin',
            'email_suffix'
        ]


class GroupSerializer(serializers.ModelSerializer):
    rules = RuleSerializer(source='*')

    class Meta:
        model = Group
        fields = ['id', 'name', 'rules', 'apply_hint', 'verified', 'verify_message']


class GroupApplicationSerializer(serializers.ModelSerializer):
    def validate_group(self, group):
        # 已经为组内成员不能重复申请
        user = self.context['request'].user
        if user in group.users.filter():
            raise ValidationError("You are already a member of this group")
        return group

    class Meta:
        model = Application
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Application.objects.filter(Q(status='pending') | Q(status='accepted')),
                fields=['user', 'group']
            )
        ]


class GroupApplicationUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = ['status']


class ProfileSerializer(serializers.ModelSerializer):
    user = PublicProfileSerializer(read_only=True)

    class Meta:
        model = Application
        fields = ['user', 'apply_message']
