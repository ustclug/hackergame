from user.models import User
from group.models import Group, Application


def join_group(user: User, group: Group):
    Application.objects.update_or_create(user=user, group=group, defaults={'status': 'accepted'})


def leave_group(user: User, group: Group):
    try:
        Application.objects.get(user=user, group=group, status='accepted').delete()
    except Application.DoesNotExist:
        pass
