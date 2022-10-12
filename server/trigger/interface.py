from server.user.interface import User, PermissionRequired
from server.exceptions import Error, NotFound, WrongArguments
from . import models


class TriggerIsOff(Error):
    code = 'trigger_is_off'
    message = '比赛暂时关闭'


class Trigger:
    json_fields = ('pk', 'time', 'can_view_challenges', 'can_try',
                   'can_submit', 'can_update_profile', 'note')
    update_fields = ('time', 'can_view_challenges', 'can_try',
                     'can_submit', 'can_update_profile', 'note')
    subscribers = []

    def __init__(self, context, obj: models.Trigger):
        self._context = context
        self._obj = obj

    @classmethod
    def _test(cls, context, name, default):
        try:
            obj = (
                models.Trigger.objects
                .filter(time__lte=context.time)
                .latest('time')
            )
        except models.Trigger.DoesNotExist:
            if default:
                return
            raise TriggerIsOff('比赛尚未开始')
        self = cls(context, obj)
        if not getattr(self, name):
            raise TriggerIsOff(self.note)

    @classmethod
    def test_can_view_challenges(cls, context):
        return cls._test(context, 'can_view_challenges', False)

    @classmethod
    def test_can_try(cls, context):
        return cls._test(context, 'can_try', False)

    @classmethod
    def test_can_submit(cls, context):
        return cls._test(context, 'can_submit', False)

    @classmethod
    def test_can_update_profile(cls, context):
        return cls._test(context, 'can_update_profile', True)

    @classmethod
    def create(cls, context, **kwargs):
        User.test_permission(context, 'trigger.full')
        self = cls(context, models.Trigger())
        self._update(**kwargs)
        new = self._json_all
        for subscriber in self.subscribers:
            subscriber(None, new)
        return self

    @classmethod
    def get(cls, context, pk):
        User.test_permission(context, 'trigger.full')
        try:
            return cls(context, models.Trigger.objects.get(pk=pk))
        except models.Trigger.DoesNotExist:
            raise NotFound()

    @classmethod
    def get_all(cls, context):
        queryset = models.Trigger.objects.order_by('time')
        try:
            User.test_permission(context, 'trigger.full')
        except PermissionRequired:
            queryset = queryset.filter(time__lte=context.time)
        return [cls(context, obj) for obj in queryset]

    def update(self, **kwargs):
        User.test_permission(self._context, 'trigger.full')
        old = self._json_all
        self._update(**kwargs)
        new = self._json_all
        for subscriber in self.subscribers:
            subscriber(old, new)

    def _update(self, **kwargs):
        for k, v in kwargs.items():
            if k in {'note'}:
                v = v or None
                setattr(self._obj, k, v)
            elif k in {'time', 'can_view_challenges', 'can_try', 'can_submit', 'can_update_profile'}:
                setattr(self._obj, k, v)
            else:
                raise WrongArguments()
        self._obj.save()
        self._obj.refresh_from_db()

    def delete(self):
        User.test_permission(self._context, 'trigger.full')
        self._obj.delete()
        self._obj = None

    @property
    def json(self):
        result = {}
        for i in self.json_fields:
            try:
                result[i] = getattr(self, i)
            except PermissionRequired:
                pass
        return result

    @property
    def _json_all(self):
        return type(self)(self._context.copy(elevated=True), self._obj).json

    @property
    def pk(self):
        return self._obj.pk

    @property
    def time(self):
        return self._obj.time

    @property
    def can_view_challenges(self):
        return self._obj.can_view_challenges

    @property
    def can_try(self):
        return self._obj.can_try

    @property
    def can_submit(self):
        return self._obj.can_submit

    @property
    def can_update_profile(self):
        return self._obj.can_update_profile

    @property
    def note(self):
        return self._obj.note
