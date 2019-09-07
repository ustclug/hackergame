from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import generic

from .models import Token


class GetToken(LoginRequiredMixin, generic.View):
    raise_exception = True

    @staticmethod
    def get(request):
        messages.info(request, 'Token: ' + Token.get(request.user).token)
        return redirect(settings.TOKEN_REDIRECT_URL)
