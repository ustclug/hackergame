from datetime import timedelta
import json
import re

from django.contrib import messages
from django.contrib.auth import login
from django.core.validators import EmailValidator, ValidationError
from django.http.response import JsonResponse
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views import View

from server.user.interface import User
from server.context import Context
from ..models import Account, Code


class DomainEmailValidator(EmailValidator):
    message = '邮箱格式错误'

    def __init__(self, domains, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(domains, str):
            domains = [domains]
        self.domains = set(domains)

    def validate_domain_part(self, domain_part):
        return domain_part in self.domains
    
    
class RegexDomainEmailValidator(EmailValidator):
    message = '邮箱格式错误'
    
    def __init__(self, domain_regex, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.domain_regex = re.compile(domain_regex, re.IGNORECASE)
        
    def validate_domain_part(self, domain_part: str) -> bool:
        return self.domain_regex.match(domain_part)
    

class UserRegexAndDomainEmailValidator(DomainEmailValidator):
    def __init__(self, domains, user_regex, *args, **kwargs):
        super().__init__(domains, *args, **kwargs)
        self.user_regex = re.compile(user_regex, re.IGNORECASE)


class AllowlistEmailValidator():
    message = '邮箱格式错误'
    code = 'invalid'

    def __init__(self, allowlist):
        self.allowlist = allowlist
        
    def __call__(self, value):
        if not value or value not in self.allowlist:
            raise ValidationError(self.message, code=self.code, params={'value': value})


class BaseLoginView(View):
    backend = 'django.contrib.auth.backends.ModelBackend'
    template_name: str
    template_context = None
    provider: str
    group: str
    identity: str
    code: str

    def get(self, request):
        return TemplateResponse(request, self.template_name,
                                self.template_context)

    def post(self, request):
        if self.check_code():
            self.login()
        return redirect('hub')

    def check_code(self):
        self.identity = self.request.POST.get('identity')
        self.code = self.request.POST.get('code')
        if Code.authenticate(self.provider, self.identity, self.code):
            return True
        messages.error(self.request, '校验码错误')
        return False

    def on_get_account(self, account):
        pass

    def normalize_identity(self):
        return self.identity

    def login(self, **kwargs):
        account, created = Account.objects.get_or_create(
            provider=self.provider,
            identity=self.normalize_identity(),
        )
        self.on_get_account(account)
        if not account.user:
            account.user = User.create(
                Context(elevated=True),
                group=self.group,
                **kwargs,
            ).user
            account.save()
        login(self.request, account.user, self.backend)


class BaseGetCodeView(View):
    provider: str
    duration = timedelta(minutes=10)

    def post(self, request):
        identity = json.loads(request.body).get('identity')
        try:
            self.validate_identity(identity)
        except ValidationError as e:
            return JsonResponse({'error': e.message}, status=400)
        try:
            code = Code.generate(self.provider, identity, self.duration)
        except Code.TooMany:
            return JsonResponse({'error': '校验码发送过于频繁'}, status=429)
        # noinspection PyBroadException
        try:
            self.send(identity, code)
        except Exception:
            # invalidate code
            Code.authenticate(self.provider, identity, code)
            return JsonResponse({'error': '校验码发送失败'}, status=400)
        return JsonResponse({})

    def validate_identity(self, identity):
        pass

    def send(self, identity, code):
        raise NotImplementedError
