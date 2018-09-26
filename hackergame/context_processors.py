from django.conf import settings


def site(request):
    _ = request
    return {'site': settings.SITE}
