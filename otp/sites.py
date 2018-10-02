from django.conf import settings
from django.urls import include, path
from django.utils.module_loading import import_string


class OtpSite:
    def __init__(self, name='otp'):
        self.name = name
        self.backends = [import_string(backend)() for backend in settings.OTP_BACKENDS]

    @property
    def urls(self):
        return (
            [path(f'{backend.id}/', include(backend.urls)) for backend in self.backends],
            'otp',
            self.name,
        )


site = OtpSite()
