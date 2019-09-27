from . import site


def otp(request):
    _ = request
    return {'otp_backends': site.backends}
