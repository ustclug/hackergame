from django.contrib.auth.models import AnonymousUser
from django.utils.timezone import now

from django.http import HttpRequest
from django.contrib.auth.models import User
from datetime import datetime
from typing import Optional, Union


class Context:
    def __init__(self, user: Optional[Union[User, AnonymousUser]] = None, 
                 time: Optional[datetime] = None, elevated: bool = False):
        self.user = user or AnonymousUser()
        self.time = time or now()
        self.elevated = elevated
        self.permissions: dict[str, bool] = {}

    @classmethod
    def from_request(cls, request: HttpRequest) -> 'Context':
        return cls(request.user)

    # Django's has_perm() is too expensive.
    def has_perm(self, permission: str) -> bool:
        if permission not in self.permissions:
            self.permissions[permission] = self.user.has_perm(permission)
        return self.permissions[permission]

    def copy(self, **kwargs) -> 'Context':
        d = {'user': self.user, 'time': self.time, 'elevated': self.elevated}
        d.update(kwargs)
        return type(self)(**d)  # type: ignore
