import json

from django.conf import settings
from django.core.validators import RegexValidator
from django.shortcuts import redirect
from django.urls import path

import aliyunsdkcore.acs_exception.exceptions
import aliyunsdkcore.client
import aliyunsdkcore.request

from .base import BaseLoginView, BaseGetCodeView

client = aliyunsdkcore.client.AcsClient(
    settings.SMS_ACCESS_KEY_ID,
    settings.SMS_ACCESS_KEY_SECRET,
    'default',
)


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
        request = aliyunsdkcore.request.CommonRequest()
        request.set_accept_format('json')
        request.set_domain('dysmsapi.aliyuncs.com')
        request.set_method('POST')
        request.set_protocol_type('https')
        request.set_version('2017-05-25')
        request.set_action_name('SendSms')
        request.add_query_param('RegionId', 'default')
        request.add_query_param('PhoneNumbers', identity)
        request.add_query_param('SignName', 'Hackergame')
        request.add_query_param('TemplateCode', 'SMS_168560438')
        request.add_query_param('TemplateParam', json.dumps({'code': code}))
        response = json.loads(client.do_action_with_exception(request))
        if response['Code'] != 'OK':
            raise ValueError(response['Code'])


urlpatterns = [
    path('sms/login/', LoginView.as_view()),
    path('sms/get_code/', GetCodeView.as_view()),
]
