from django.core.validators import EmailValidator

from .email import Email


class Login(Email.LoginView):
    template_name = 'otp/edu_email.html'


class EduEmailValidator(EmailValidator):
    def __init__(self, blacklist, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(blacklist, str):
            blacklist = [blacklist]
        self.blacklist = set(blacklist)

    def validate_domain_part(self, domain_part):
        if domain_part in self.blacklist:
            return False
        domain_part = domain_part.lower()
        result = domain_part.endswith([
            '.edu.cn',
            '.edu.hk',
            '.edu.mo',
            '.edu.tw',
            '.edu.my',
        ])
        return result


class GetChallenge(Email.GetChallengeView):
    identity_validator = EduEmailValidator([
        'hnu.edu.cn',
        'smail.nju.edu.cn',
        'njust.edu.cn',
        'sjtu.edu.cn',
        'std.uestc.edu.cn',
        'ustc.edu.cn',
        'mail.ustc.edu.cn',
        'zju.edu.cn',
    ])


class EduEmail(Email):
    name = '其他高校'
    LoginView = Login
    GetChallengeView = GetChallenge
