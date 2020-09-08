from django.shortcuts import get_object_or_404
from django.http import Http404
from rest_framework import mixins
from rest_framework.generics import GenericAPIView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import NotFound
from rest_framework.permissions import BasePermission
from rest_framework.throttling import UserRateThrottle

from challenge.models import Challenge
from submission.models import Submission, ChallengeFirstBlood, SubChallengeFirstBlood, \
                            Scoreboard, ChallengeClear
from submission.serializer import SubmissionSerializer, ScoreboardSerializer, \
                            ChallengeFirstBloodSerializer, SubChallengeFirstBloodSerializer
from group.models import Group
from group.permissions import IsInGroup
from contest.models import Stage


class IsSubmissionAllowed(BasePermission):
    message = '比赛当前阶段无法提交'

    def has_permission(self, request, view):
        return Stage.objects.current_status in ('underway', 'practice')


class SubmissionAPI(APIView):
    permission_classes = APIView.permission_classes + [IsSubmissionAllowed]
    throttle_classes = [UserRateThrottle]

    def post(self, request):
        serializer = SubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            challenge = get_object_or_404(Challenge, id=data['challenge'])
        except Http404:
            raise NotFound("题目不存在")
        flag = data['flag']

        submission = Submission.objects.create(user=request.user, challenge=challenge, flag=flag)

        if submission.correctness is True:
            msg = 'correct'
        else:
            msg = 'wrong'
        return Response({'detail': msg})


class ScoreboardAPI(GenericAPIView, mixins.ListModelMixin):
    serializer_class = ScoreboardSerializer
    permission_classes = GenericAPIView.permission_classes + [IsInGroup]
    # TODO: 做题历史, 进度

    def get_queryset(self):
        params = self.request.query_params
        scoreboard = Scoreboard.objects.filter(category=params.get('category', ''))
        group = params.get('group')
        if group:
            group = get_object_or_404(Group, pk=group)
            self.check_object_permissions(self.request, group)
            return scoreboard.filter(user__application__status='accepted', user__application__group=group)
        else:
            return scoreboard

    def get(self, request, *args, **kwargs):
        response = self.list(request, *args, **kwargs)
        return response


class FirstBloodBoardAPI(APIView):
    def get(self, request):
        group = self.request.query_params.get('group')
        if group:
            group = get_object_or_404(Group, pk=group)
            self.check_object_permissions(self.request, group)
        return Response({
            'challenges': ChallengeFirstBloodSerializer(
                ChallengeFirstBlood.objects.filter(group=group),
                many=True
            ).data,
            'sub_challenges': SubChallengeFirstBloodSerializer(
                SubChallengeFirstBlood.objects.filter(group=group),
                many=True
            ).data
        })


class ChallengeClearAPI(APIView):
    def get(self, request):  # 可能有性能问题
        challenges = Challenge.objects.filter(sub_challenge__enabled=True).distinct()
        rtn = []
        for challenge in challenges:
            data = {
                'challenge': challenge.id,
                'clear': ChallengeClear.objects.filter(challenge=challenge, user=request.user).exists(),
                'sub_challenges': []
            }
            sub_challenge_clear = Submission.objects.filter(
                challenge=challenge,
                user=request.user,
                sub_challenge_clear__isnull=False).values_list('sub_challenge_clear', flat=True)
            for sub_challenge in challenge.sub_challenge.all():
                s = {'sub_challenge': sub_challenge.id, 'clear': False}
                if sub_challenge.id in sub_challenge_clear:
                    s['clear'] = True
                data['sub_challenges'].append(s)
            rtn.append(data)
        return Response(rtn)
