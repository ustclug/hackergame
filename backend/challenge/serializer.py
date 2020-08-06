from rest_framework import serializers

from challenge.models import SubChallenge, Challenge


class EnabledSubChallenge(serializers.ListSerializer):
    def to_representation(self, data):
        data = data.filter(enabled=True)
        return super().to_representation(data)


class SubChallengeSerializer(serializers.ModelSerializer):
    class Meta:
        list_serializer_class = EnabledSubChallenge
        model = SubChallenge
        fields = ['id', 'name', 'score']


class ChallengeSerializer(serializers.ModelSerializer):
    sub_challenge = SubChallengeSerializer(many=True, read_only=True)

    class Meta:
        model = Challenge
        fields = ['id', 'name', 'category', 'detail', 'prompt', 'sub_challenge']
