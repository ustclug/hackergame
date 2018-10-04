from .email import Email, DomainEmailValidator


class GetChallenge(Email.GetChallengeView):
    identity_validator = DomainEmailValidator('smail.nju.edu.cn')


class Nju(Email):
    name = '南京大学'
    GetChallengeView = GetChallenge
