from rest_framework.generics import ListAPIView
from rest_framework.permissions import BasePermission

from challenge.models import Challenge
from challenge.serializer import ChallengeSerializer
from contest.models import Stage


class IsViewChallengeAllowed(BasePermission):
    message = '比赛当前阶段无法查看题目'

    def has_permission(self, request, view):
        return Stage.objects.current_status in ('underway', 'practice', 'ended')


class ChallengeAPI(ListAPIView):
    permission_classes = ListAPIView.permission_classes + [IsViewChallengeAllowed]
    queryset = Challenge.objects.filter(sub_challenge__enabled=True)
    serializer_class = ChallengeSerializer
    pagination_class = None
