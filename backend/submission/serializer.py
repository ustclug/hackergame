from rest_framework import serializers

from submission.models import Scoreboard, ChallengeFirstBlood, SubChallengeFirstBlood, Submission


class SubmissionSerializer(serializers.Serializer):
    challenge = serializers.IntegerField()
    flag = serializers.CharField(max_length=200)


class ScoreboardSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scoreboard
        fields = ['user', 'score', 'time']


class ChallengeFirstBloodSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChallengeFirstBlood
        fields = ['challenge', 'user', 'time']


class SubChallengeFirstBloodSerializer(serializers.ModelSerializer):
    challenge = serializers.PrimaryKeyRelatedField(source='sub_challenge.challenge', read_only=True)

    class Meta:
        model = SubChallengeFirstBlood
        fields = ['sub_challenge', 'challenge', 'user', 'time']


class ChallengeClearSerializer(serializers.ModelSerializer):
    clear = serializers.BooleanField(source='challenge_clear')


    class Meta:
        model = Submission
        fields = ['challenge', 'clear', 'sub_challenges']

