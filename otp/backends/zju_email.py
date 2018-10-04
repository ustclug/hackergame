from .email import Email, DomainEmailValidator


class GetChallenge(Email.GetChallengeView):
    identity_validator = DomainEmailValidator('zju.edu.cn')


class Zju(Email):
    name = '浙江大学'
    GetChallengeView = GetChallenge
