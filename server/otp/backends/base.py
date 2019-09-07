from django.urls import reverse
from django.utils.decorators import classproperty
from django.utils.text import camel_case_to_spaces


class Backend:
    @classproperty
    def id(cls):
        return cls.__name__.lower()

    @classproperty
    def name(cls):
        return camel_case_to_spaces(cls.__name__)

    @classproperty
    def urls(cls):
        raise NotImplementedError

    @classproperty
    def login_url(cls):
        return reverse(f'otp:{cls.id}')
