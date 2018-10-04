from .email import Email, DomainEmailValidator


class GetChallenge(Email.GetChallengeView):
    identity_validator = DomainEmailValidator('njust.edu.cn')


class Njust(Email):
    name = '南京理工大学'
    GetChallengeView = GetChallenge
