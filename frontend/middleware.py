import logging
from django.utils.deprecation import MiddlewareMixin


request_logger = logging.getLogger('django.request')


class UserRequestMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        super().__init__(get_response)

    def process_response(self, request, response):
        request_logger.info(msg=f"{request.get_full_path()}", extra={"request": request})
        return response
