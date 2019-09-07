from .email import Email, DomainEmailValidator


class GetChallenge(Email.GetChallengeView):
    identity_validator = DomainEmailValidator('hnu.edu.cn')


class Hnu(Email):
    name = '湖南大学'
    GetChallengeView = GetChallenge
