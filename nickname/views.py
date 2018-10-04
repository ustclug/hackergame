from hashlib import sha3_256
import json
from uuid import UUID

from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.views import generic


class Nickname(generic.View):
    @staticmethod
    def get(request):
        try:
            UUID(request.user.username)
        except ValueError:
            return redirect(settings.NICKNAME_REDIRECT_URL)
        try:
            prefix = request.user.device_set.all()[0].identity
        except IndexError:
            prefix = ''
        if '@' in prefix:
            prefix = prefix[:prefix.find('@')]
        postfix = sha3_256(f'{request.user.pk}/{settings.SECRET_KEY}'.encode()).hexdigest()[:4]
        return render(request, 'nickname/change.html', {'context': {'prefix': prefix, 'postfix': postfix}})

    @staticmethod
    def post(request):
        prefix = json.loads(request.body)['prefix']
        postfix = sha3_256(f'{request.user.pk}/{settings.SECRET_KEY}'.encode()).hexdigest()[:4]
        request.user.username = prefix + '.' + postfix
        try:
            request.user.full_clean()
        except ValidationError:
            return JsonResponse({'error': 'wrong username'}, status=400)
        request.user.save()
        return JsonResponse({})
