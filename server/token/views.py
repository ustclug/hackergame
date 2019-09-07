import base64
import OpenSSL

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views import generic

from .models import Token


class GetToken(LoginRequiredMixin, generic.View):
    raise_exception = True
    private_key = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM,
                                                 settings.PRIVATE_KEY)

    def get(self, request):
        try:
            messages.info(request, 'Token: ' + request.user.token.token)
        except Token.DoesNotExist:
            id = str(request.user.pk)
            sig = OpenSSL.crypto.sign(self.private_key, id.encode(), 'sha256')
            token = id + ':' + base64.b64encode(sig).decode()
            Token.objects.create(user=request.user, token=token)
            messages.info(request, 'Token: ' + request.user.token.token)
        return redirect(settings.TOKEN_REDIRECT_URL)
