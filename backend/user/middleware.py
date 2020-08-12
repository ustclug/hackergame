from django.contrib.auth import logout


class LogoutBannedUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    def __call__(self, request):
        if request.user.groups.filter(name='banned').exists():
            logout(request)

        response = self.get_response(request)  # call the view

        return response
