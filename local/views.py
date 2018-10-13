from django.contrib.auth.mixins import UserPassesTestMixin
from django.views import generic

from ctf.models import CtfInfo
from .models import UstcFirstBlood


class FirstBlood(UserPassesTestMixin, generic.ListView):
    model = UstcFirstBlood
    raise_exception = True
    template_name = 'local/first_blood.html'

    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
        return CtfInfo(self.request.user).first_backend.id == 'ustc'
