import time
import logging

from django.contrib.auth import logout


logger = logging.getLogger(__name__)


class LogoutBannedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        if request.user.groups.filter(name='banned').exists():
            logout(request)

        response = self.get_response(request)  # call the view

        return response


# TODO: 移动到一个合适的位置
class StatMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        start_time = time.time()

        response = self.get_response(request)

        duration = time.time() - start_time
        if duration > 0.3:
            logger.warning(f'Process time for Request {request.path}: {duration:.4}s')

        return response
