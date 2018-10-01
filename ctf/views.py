from django.conf import settings
from django.contrib import messages
from django.db.transaction import atomic
from django.views import generic
from django.shortcuts import redirect

from .models import Problem, Flag, Solve, Log


class Hub(generic.ListView):
    template_name = settings.CTF_TEMPLATE_HUB

    def get_queryset(self):
        return Problem.annotated(Problem.open_objects)

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
