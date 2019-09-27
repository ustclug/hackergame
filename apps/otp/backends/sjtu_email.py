from .email import Email, DomainEmailValidator


class GetChallenge(Email.GetChallengeView):
    identity_validator = DomainEmailValidator('sjtu.edu.cn')


class Sjtu(Email):
    name = '上海交通大学'
    GetChallengeView = GetChallenge
