from django.shortcuts import get_object_or_404
from django.db.models import F
from django.http import Http404
from rest_framework import generics, mixins
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound

from challenge.models import Challenge
from submission.models import Submission, ChallengeFirstBlood, SubChallengeFirstBlood, Scoreboard
from submission.serializer import SubmissionSerializer, ScoreboardSerializer, \
                            ChallengeFirstBloodSerializer, SubChallengeFirstBloodSerializer
from group.models import Group
from group.permissions import IsInGroup
from user.models import User


class SubmissionAPI(APIView):
    permission_classes = [IsAuthenticated]  # TODO: deal with banned user

    def post(self, request):
        serializer = SubmissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            challenge = get_object_or_404(Challenge, id=data['challenge'])
        except Http404:
            raise NotFound("The challenge does not exist.")
        flag = data['flag']

        submission = Submission.objects.create(user=request.user, challenge=challenge, flag=flag)

        # 检查提交是否正确
        correct = submission.update_clear_status()

        submission.update_board()

        if correct:
            msg = 'correct'
        else:
            msg = 'wrong'
        return Response({'detail': msg})


class ScoreboardAPI(generics.GenericAPIView, mixins.ListModelMixin):
    serializer_class = ScoreboardSerializer
    permission_classes = [IsInGroup]
    # TODO: 做题历史, 进度

    def get_queryset(self):
        params = self.request.query_params
        scoreboard = Scoreboard.objects.filter(category=params.get('category', ''))
        group = params.get('group')
        if group:
            group = get_object_or_404(Group, pk=group)
            self.check_object_permissions(self.request, group)
            return scoreboard.filter(user__in=group.users)
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
