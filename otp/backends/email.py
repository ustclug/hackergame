from smtplib import SMTPException

from django.core.validators import EmailValidator
from django.core.mail import EmailMessage
from django.http import JsonResponse
from django.template.loader import render_to_string

from .console import Console


class DomainEmailValidator(EmailValidator):
    def __init__(self, domains, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(domains, str):
            domains = [domains]
        self.domains = set(domains)

    def validate_domain_part(self, domain_part):
        return domain_part in self.domains


class Login(Console.LoginView):
    template_name = 'otp/email.html'


class GetChallenge(Console.GetChallengeView):
    identity_validator = EmailValidator()
    email_subject_template = 'otp/email/subject.txt'
    email_body_template = 'otp/email/body.txt'

    def send(self, token):
        context = {'token': token.token}
        subject = render_to_string(self.email_subject_template, context=context)
        subject = ''.join(subject.splitlines())
        body = render_to_string(self.email_body_template, context=context)
        try:
            EmailMessage(subject=subject, body=body, to=[token.device.identity]).send()
        except SMTPException:
            return JsonResponse({'error': 'fail'})
        return JsonResponse({})


class Email(Console):
    name = '其他'
    LoginView = Login
    GetChallengeView = GetChallenge
