from datetime import timedelta
import json

from django.conf import settings
from django.core.exceptions import ValidationError
from django.http import JsonResponse

import aliyunsdkcore.acs_exception.exceptions
import aliyunsdkcore.client
import aliyunsdkcore.request

from .console import Console

client = aliyunsdkcore.client.AcsClient(settings.SMS_ACCESS_KEY_ID,
    settings.SMS_ACCESS_KEY_SECRET, 'default')


class Login(Console.LoginView):
    template_name = 'otp/sms.html'


class GetChallenge(Console.GetChallengeView):
    @staticmethod
    def identity_validator(identity):
        try:
            assert isinstance(identity, str), 'not str'
            assert all(c in '0123456789' for c in identity), 'not digits'
            assert len(identity) == 11, 'not 11 digits'
            assert identity[0] == '1', 'not starts with 1'
        except AssertionError as e:
            raise ValidationError(f'{identity!r}: {e.args[0]}')

    @staticmethod
    def send(token):
        request = aliyunsdkcore.request.CommonRequest()
        request.set_accept_format('json')
        request.set_domain('dysmsapi.aliyuncs.com')
        request.set_method('POST')
        request.set_protocol_type('https')
        request.set_version('2017-05-25')
        request.set_action_name('SendSms')
        request.add_query_param('RegionId', 'default')
        request.add_query_param('PhoneNumbers', token.device.identity)
        request.add_query_param('SignName', 'Hackergame')
        request.add_query_param('TemplateCode', 'SMS_168560438')
        request.add_query_param('TemplateParam', json.dumps({
            'code': token.token,
        }))
        response = json.loads(client.do_action_with_exception(request))
        print(response)
        if response['Code'] == 'OK':
            return JsonResponse({})
        else:
            return JsonResponse({'error': 'fail'}, status=500)


class Sms(Console):
    name = '其他'
    LoginView = Login
    GetChallengeView = GetChallenge
