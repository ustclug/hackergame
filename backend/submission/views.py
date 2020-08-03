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
from submission.serializer import SubmissionSerializer
from group.models import Group
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
        # 判断重复提交
        if Submission.objects.filter(user=request.user, challenge=challenge, flag=flag,
                                     sub_challenge_clear=True).exists():
            repeat = True
        else:
            repeat = False

        submission = Submission.objects.create(user=request.user, challenge=challenge, flag=flag)

        # 检查提交是否正确
        correct = False
        for sub_challenge in challenge.sub_challenge.filter(enabled=True):
            if sub_challenge.check_correctness(flag, request.user):
                correct = True
                if not repeat:
                    submission.sub_challenge_clear = sub_challenge
            violation_user = sub_challenge.check_violation(flag, request.user)
            if violation_user is not None:
                submission.violation_user = violation_user
        submission.save()

        if submission.sub_challenge_clear is not None:
            correct_challenge_submission = Submission.objects.filter(challenge=challenge, user=request.user,
                                                                     sub_challenge_clear__isnull=False)
            if correct_challenge_submission.count() == challenge.sub_challenge.count():
                submission.challenge_clear = True
        submission.save()

        # 更新榜单
        if submission.sub_challenge_clear and not request.user.groups.filter(name='no_score').exists():
            for group in Group.objects.filter(application__user=request.user, application__status='accepted'):
                # 一血榜
                SubChallengeFirstBlood.objects.get_or_create(sub_challenge=submission.sub_challenge_clear,
                                                             group=group, defaults={'user': request.user})
                if submission.challenge_clear:
                    ChallengeFirstBlood.objects.get_or_create(challenge=challenge, group=group,
                                                              defaults={'user': request.user})

            # 分数榜
            self.update_scoreboard(request.user, submission)
            self.update_scoreboard(request.user, submission, challenge.category)

        if correct:
            msg = 'correct'
        else:
            msg = 'wrong'
        return Response({'detail': msg})

    def update_scoreboard(self, user: User, submission: Submission, category: str = ''):
        """更新分数榜, 若分类为空则为总榜"""
        try:
            scoreboard = Scoreboard.objects.get(user=user, category=category)
            scoreboard.score = F('score') + submission.sub_challenge_clear.score
            scoreboard.time = submission.created_time
            scoreboard.save()
        except Scoreboard.DoesNotExist:
            Scoreboard.objects.create(
                user=user,
                category=category,
                score=submission.sub_challenge_clear.score,
                time=submission.created_time
            )


class BoardAPI(generics.GenericAPIView, mixins.ListModelMixin):
    def get_queryset(self):
        params = self.request.query_params
        return Scoreboard.objects.all()
