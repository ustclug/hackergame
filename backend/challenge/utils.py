import base64 as b64
import hashlib

functions = {'hashlib': hashlib}


def _base64(s):
    if isinstance(s, str):
        s = s.encode()
    return b64.b64encode(s).decode()


functions['base64'] = _base64

for method in ('md5', 'sha1', 'sha224', 'sha256', 'sha384', 'sha512',
               'sha3_224', 'sha3_256', 'sha3_384', 'sha3_512'):
    def f(s, method=method):
        if isinstance(s, str):
            s = s.encode()
        return getattr(hashlib, method)(s).hexdigest()

    functions[method] = f


def eval_token_expression(expr, token):
    return eval(expr, functions, {'token': token})
