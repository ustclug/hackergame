from .email import Email, DomainEmailValidator


class GetChallenge(Email.GetChallengeView):
    identity_validator = DomainEmailValidator('mail.nankai.edu.cn')


class Nankai(Email):
    name = '南开大学'
    GetChallengeView = GetChallenge
