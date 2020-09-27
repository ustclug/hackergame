import time
import logging


logger = logging.getLogger(__name__)


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
