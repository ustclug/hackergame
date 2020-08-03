from rest_framework import serializers

from submission.models import Scoreboard


class SubmissionSerializer(serializers.Serializer):
    challenge = serializers.IntegerField()
    flag = serializers.CharField(max_length=200)


class ScoreboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scoreboard
        fields = ['user', 'score', 'time']
