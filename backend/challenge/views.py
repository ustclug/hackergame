from rest_framework import generics
from rest_framework.mixins import ListModelMixin
from rest_framework.exceptions import ValidationError

from challenge.models import Challenge
from challenge.serializer import ChallengeSerializer
from contest.models import Stage


class ChallengeAPI(generics.GenericAPIView, ListModelMixin):
    queryset = Challenge.objects.filter(sub_challenge__enabled=True)
    serializer_class = ChallengeSerializer

    def get(self, request):
        if Stage.objects.current_status in ('not start', 'paused'):
            raise ValidationError("You can not view problems in the current stage.")
        return self.list(request)
