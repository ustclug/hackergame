import base64
import uuid

import OpenSSL

from django.conf import settings

_private_key = OpenSSL.crypto.load_privatekey(
    OpenSSL.crypto.FILETYPE_PEM, settings.PRIVATE_KEY)


def generate_uuid_and_token() -> (str, str):
    uid = str(uuid.uuid1())
    sig = base64.b64encode(OpenSSL.crypto.sign(
        _private_key, uid.encode(), 'sha256')).decode()
    return uid, sig
