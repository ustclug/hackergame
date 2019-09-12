from hashlib import sha3_256

from django.conf import settings


def postfix(user):
    key = f'{user.pk}/{settings.SECRET_KEY}'
    return sha3_256(key.encode()).hexdigest()[:4]
