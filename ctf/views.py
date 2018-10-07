from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.db.transaction import atomic
from django.views import generic
from django.shortcuts import redirect

import otp
from terms.mixins import TermsRequiredMixin
from .models import TimerSwitch, Problem, Flag, Solve, Log, UserScoreCache


class Hub(TermsRequiredMixin, generic.ListView):
    template_name = settings.CTF_TEMPLATE_HUB

    def get_queryset(self):
        queryset = Problem.open_objects
        if not (TimerSwitch.is_on_now() or self.request.user.has_perm('ctf.view_problem')):
            queryset = queryset.none()
        return queryset.prefetch_related('flag_set')

    @staticmethod
    def post(request):
        with atomic():
            try:
                problem = Problem.open_objects.get(pk=request.POST['problem'])
            except Problem.DoesNotExist:
                messages.error(request, '题目不存在')
                return redirect('hub')
            try:
                flag = problem.flag_set.get(flag=request.POST['flag'])
            except Flag.DoesNotExist:
                flag = None
            user = request.user if request.user.is_authenticated else None
            Log.objects.create(user=user, problem=problem, flag=request.POST['flag'], match=flag)
            if flag:
                if user:
                    messages.success(request, '答案正确')
                    Solve.objects.get_or_create(user=user, flag=flag)
                else:
                    messages.success(request, '答案正确（但您未登录，结果将不会被记录）')
            else:
                messages.error(request, '答案错误')
            return redirect('hub')


class Board(PermissionRequiredMixin, generic.ListView):
    permission_required = 'ctf.view_userscorecache'
    raise_exception = True
    template_name = settings.CTF_TEMPLATE_BOARD

    def get_queryset(self):
        queryset = UserScoreCache.objects.filter(score__gt=0).order_by('-score', 'time')
        if 'backend' in self.kwargs:
            queryset = queryset.filter(user__device__backend=self.kwargs['backend'])
        return queryset[:100]

    def get_context_data(self, **kwargs):
        if 'backend' in self.kwargs:
            backend = otp.site.backends_dict[self.kwargs['backend']]
        else:
            backend = None
        total_score = Problem.total_score
        return super().get_context_data(backend=backend, total_score=total_score, **kwargs)
