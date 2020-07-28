from rest_framework import serializers

from challenge.models import SubChallenge, Challenge


class SubChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubChallenge
        fields = ['id', 'name', 'score']


class ChallengeSerializer(serializers.ModelSerializer):
    sub_challenge = SubChallengeSerializer(many=True, read_only=True)

    class Meta:
        model = Challenge
        fields = ['id', 'name', 'category', 'detail', 'prompt', 'sub_challenge']
