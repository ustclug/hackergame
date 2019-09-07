from django.contrib import messages
from django.core.exceptions import ValidationError, PermissionDenied
from django.shortcuts import redirect

from .dummy import Dummy
from .email import DomainEmailValidator


class DomainBlacklistEmailValidator(DomainEmailValidator):
    def validate_domain_part(self, domain_part):
        return domain_part not in self.domains


class Login(Dummy.LoginView):
    template_name = 'otp/dummy_email.html'
    identity_validator = DomainBlacklistEmailValidator([
        'hnu.edu.cn',
        'smail.nju.edu.cn',
        'njust.edu.cn',
        'sjtu.edu.cn',
        'std.uestc.edu.cn',
        'ustc.edu.cn',
        'mail.ustc.edu.cn',
        'zju.edu.cn',
    ])
    validation_error_message = '联盟学校参赛者请从相应学校的登录入口登录，其他参赛者请输入正确的电子邮箱地址。'

    def post(self, request):
        identity = request.POST['identity']
        try:
            self.identity_validator(identity)
        except ValidationError:
            messages.error(request, self.validation_error_message)
            return redirect(self.backend.login_url)
        return super().post(request)

    @staticmethod
    def create_user(device):
        raise PermissionDenied


class DummyEmail(Dummy):
    id = 'email'
    name = '其他'
    LoginView = Login
