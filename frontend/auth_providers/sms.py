import json

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login
from django.http.response import JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path
from django.views import View

import aliyunsdkcore.acs_exception.exceptions
import aliyunsdkcore.client
import aliyunsdkcore.request

from server.user.interface import User
from server.context import Context
from ..models import Account, Code

backend = 'django.contrib.auth.backends.ModelBackend'
client = aliyunsdkcore.client.AcsClient(
    settings.SMS_ACCESS_KEY_ID,
    settings.SMS_ACCESS_KEY_SECRET,
    'default',
)


# noinspection PyMethodMayBeStatic
class LoginView(View):
    def get(self, request):
        return TemplateResponse(request, 'login_sms.html')

    def post(self, request):
        identity = request.POST.get('identity')
        code = request.POST.get('code')
        if not Code.authenticate('sms', identity, code):
            messages.error(request, '校验码错误')
            return redirect('hub')
        account, created = Account.objects.get_or_create(
            provider='sms',
            identity=identity,
        )
        if not account.user:
            account.user = User.create(
                Context.from_request(request),
                group='other',
                nickname=identity,
                tel=identity,
            ).user
            account.save()
        login(request, account.user, backend)
        return redirect('hub')


# noinspection PyMethodMayBeStatic
class GetCodeView(View):
    def post(self, request):
        identity = json.loads(request.body).get('identity')
        try:
            assert isinstance(identity, str)
            assert all(c in '0123456789' for c in identity)
            assert len(identity) == 11
            assert identity[0] == '1'
        except AssertionError:
            return JsonResponse({'error': '手机号码格式错误'}, status=400)
        try:
            code = Code.generate('sms', identity)
        except Code.TooMany:
            return JsonResponse({'error': '校验码发送过于频繁'}, status=429)
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
        request.add_query_param('TemplateParam', json.dumps({
            'code': code.code,
        }))
        response = json.loads(client.do_action_with_exception(request))
        print(response)
        if response['Code'] == 'OK':
            return JsonResponse({})
        else:
            return JsonResponse({'error': '校验码发送失败'}, status=400)


urlpatterns = [
    path('sms/login/', LoginView.as_view()),
    path('sms/get_code/', GetCodeView.as_view()),
]
