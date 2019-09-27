from server.user.interface import User
from server.context import Context

from .models import Page


def frontend(request):
    return {
        'page': Page.get(),
        'user_': (
            User.get(Context.from_request(request), request.user.pk)
            if request.user.is_authenticated else None
        ),
    }
