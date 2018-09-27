from .models import TimerSwitch, CtfInfo


def info(request):
    return {'ctf_info': CtfInfo(request.user)}


def switch(request):
    _ = request
    return {'ctf_switch': TimerSwitch.is_on_now}
