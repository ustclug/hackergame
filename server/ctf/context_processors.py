from .models import Page, TimerSwitch, CtfInfo


def ctf(request):
    return {
        'ctf_info': CtfInfo(request.user),
        'ctf_switch': TimerSwitch.is_on_now,
        'ctf_page': Page.load(),
    }
