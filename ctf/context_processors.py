from .models import CtfInfo


def info(request):
    return {'ctf_info': CtfInfo(request.user)}
