import uuid

from django.core.signing import Signer

_signer = Signer()


def generate_uuid_and_token() -> (str, str):
    uid = str(uuid.uuid1())
    sig = _signer.sign(uid)
    return uid, sig
