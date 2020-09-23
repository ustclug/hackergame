from django.shortcuts import get_object_or_404
from django.http import Http404
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


def get_progress(user):
    subs_clear = Submission.objects.filter(
        sub_challenge_clear__isnull=False,
        sub_challenge_clear__enabled=True,
        user=user
    ).order_by('sub_challenge_clear__challenge', '-created_time')
    challenges_clear = ChallengeClear.objects.filter(user=user).values_list('challenge', flat=True)

    rtn = []
    for submission in subs_clear:
        if len(rtn) == 0 or rtn[-1]['challenge'] != submission.challenge.id:
            rtn.append({
                "challenge": submission.challenge.id,
                "clear_status": "clear" if submission.challenge.id in challenges_clear else "partly",
                "time": submission.created_time,
                "sub_challenge_clear": [
                    {
                        "sub_challenge": submission.sub_challenge_clear_id,
                        "time": submission.created_time
                    }
                ]
            })
        else:
            rtn[-1]['sub_challenge_clear'].append({
                "sub_challenge": submission.sub_challenge_clear_id,
                "time": submission.created_time
            })

    return rtn


class IsSubmissionAllowed(BasePermission):
    message = '比赛当前阶段无法提交'

    def has_permission(self, request, view):
        return Stage.objects.current_status in ('underway', 'practice') or request.user.is_superuser


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


class ScoreboardAPI(GenericAPIView):
    serializer_class = ScoreboardSerializer
    permission_classes = GenericAPIView.permission_classes + [IsInGroup]

    def get_queryset(self):
        params = self.request.query_params
        scoreboard = Scoreboard.objects.filter(category=params.get('category', '')).order_by('-score')
        group = params.get('group')
        if group:
            group = get_object_or_404(Group, pk=group)
            self.check_object_permissions(self.request, group)
            return scoreboard.filter(user__application__status='accepted', user__application__group=group)
        else:
            return scoreboard

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)

        serializer = self.get_serializer(page, many=True)
        for i, res in enumerate(serializer.data):
            serializer.data[i]['challenge_clear'] = get_progress(res['user'])
        return self.get_paginated_response(serializer.data)


class ScoreHistoryAPI(APIView):
    def get(self, request, user_id):
        score = 0
        history = []
        for i in Submission.objects.filter(
                sub_challenge_clear__isnull=False,
                sub_challenge_clear__enabled=True,
        ).order_by('created_time'):
            score += i.sub_challenge_clear.score
            history.append({'score': score, 'time': i.created_time})
        return Response(history)


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


class ChallengeProgressAPI(APIView):
    def get(self, request):
        return Response(get_progress(request.user))
