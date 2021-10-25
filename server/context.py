from django.contrib.auth.models import AnonymousUser
from django.utils.timezone import now


class Context:
    def __init__(self, user=None, time=None, elevated=False):
        self.user = user or AnonymousUser()
        self.time = time or now()
        self.elevated = elevated
        self.permissions = {}

    @classmethod
    def from_request(cls, request):
        return cls(request.user)

    # Django's has_perm() is too expensive.
    def has_perm(self, permission):
        if permission not in self.permissions:
            self.permissions[permission] = self.user.has_perm(permission)
        return self.permissions[permission]

    def copy(self, **kwargs):
        d = {'user': self.user, 'time': self.time, 'elevated': self.elevated}
        d.update(kwargs)
        return type(self)(**d)
