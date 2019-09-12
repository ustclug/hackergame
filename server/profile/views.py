import json
from uuid import UUID

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import generic

from .utils import postfix


class Profile(LoginRequiredMixin, generic.View):
    raise_exception = True

    @staticmethod
    def get(request):
        show = False
        try:
            UUID(request.user.username)
        except ValueError:
            pass
        else:
            show = True
        if not request.user.profile.ok:
            show = True
        if 'force' in request.GET:
            show = True
        if not show:
            return redirect(settings.PROFILE_REDIRECT_URL)
        prefix = request.user.username
        if '.' in prefix:
            prefix = prefix[:prefix.rfind('.')]
        else:
            try:
                prefix = request.user.device_set.all()[0].identity
                if '@' in prefix:
                    prefix = prefix[:prefix.rfind('@')]
            except IndexError:
                prefix = ''
        context = {
            'prefix': prefix,
            'postfix': postfix(request.user),
            'name': request.user.profile.name,
            'sno': request.user.profile.sno,
            'tel': request.user.profile.tel,
            'email': request.user.profile.email,
        }
        return render(request, 'profile/change.html', {'context': context})

    @staticmethod
    def post(request):
        data = json.loads(request.body)
        request.user.username = data['prefix'] + '.' + postfix(request.user)
        try:
            request.user.full_clean()
        except ValidationError:
            return JsonResponse({'error': 'wrong username'}, status=400)
        request.user.save()
        request.user.profile.name = data['name']
        request.user.profile.sno = data['sno']
        request.user.profile.tel = data['tel']
        request.user.profile.email = data['email']
        request.user.profile.save()
        return JsonResponse({})
