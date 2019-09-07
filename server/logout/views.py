from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.views import generic


class Logout(generic.TemplateView):
    template_name = 'logout/logout.html'

    @staticmethod
    def post(request):
        logout(request)
        return redirect(settings.LOGOUT_REDIRECT_URL)
