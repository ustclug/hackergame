from django.contrib.auth.models import AnonymousUser
from django.utils.timezone import now


class Context:
    def __init__(self, user=None, time=None, elevated=False):
        self.user = user or AnonymousUser()
        self.time = time or now()
        self.elevated = elevated

    @classmethod
    def from_request(cls, request):
        return cls(request.user)

    def copy(self, **kwargs):
        d = {'user': self.user, 'time': self.time, 'elevated': self.elevated}
        d.update(kwargs)
        return type(self)(**d)
