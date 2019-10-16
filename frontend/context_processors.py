from server.user.interface import User
from server.context import Context

from django.conf import settings

from .models import Page


def frontend(request):
    return {
        'page': Page.get(),
        'user_': (
            User.get(Context.from_request(request), request.user.pk)
            if request.user.is_authenticated else None
        ),
        'groups': User.groups,
        'debug': settings.DEBUG,
        'no_board_groups': User.no_board_groups,
    }
