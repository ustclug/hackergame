from django.core.validators import RegexValidator
from django.shortcuts import redirect
from django.urls import path

from .base import BaseLoginView, BaseGetCodeView


class LoginView(BaseLoginView):
    template_name = 'login_sms.html'
    provider = 'sms'
    group = 'other'

    def post(self, request):
        if self.check_code():
            self.login(tel=self.identity)
        return redirect('hub')


class GetCodeView(BaseGetCodeView):
    provider = 'sms'
    validate_identity = RegexValidator(r'^1[0-9]{10}$', '手机号码格式错误')

    def send(self, identity, code):
        raise ValueError("短信登录暂不可用，请使用其他方式注册。")


urlpatterns = [
    path('sms/login/', LoginView.as_view()),
    path('sms/get_code/', GetCodeView.as_view()),
]
