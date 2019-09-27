from .email import Email, DomainEmailValidator


class GetChallenge(Email.GetChallengeView):
    identity_validator = DomainEmailValidator('std.uestc.edu.cn')


class Uestc(Email):
    name = '电子科学技术大学'
    GetChallengeView = GetChallenge
