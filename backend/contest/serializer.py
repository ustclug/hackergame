from rest_framework import serializers

from contest.models import Stage, Pause


class PauseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pause
        fields = '__all__'


class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = '__all__'
