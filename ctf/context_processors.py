from django.db import models


class CtfInfo:
    def __init__(self, user):
        self.user = user

    @property
    def score(self):
        if self.user.is_authenticated:
            return self.user.solve_set.aggregate(score=models.Sum('flag__score'))['score']
        else:
            return 0

    @property
    def solved_flags(self):
        if self.user.is_authenticated:
            return [solve.flag_id for solve in self.user.solve_set.all()]
        else:
            return []


def info(request):
    return {'ctf_info': CtfInfo(request.user)}
