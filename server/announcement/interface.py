from typing import List, Callable

from server.user.interface import User, PermissionRequired
from server.exceptions import NotFound
from . import models


class Announcement:
    json_fields = ('pk', 'content', 'time')
    update_fields = ('content',)
    subscribers: List[Callable] = []

    def __init__(self, context, obj: models.Announcement):
        self._context = context
        self._obj = obj

    @classmethod
    def create(cls, context, content):
        User.test_permission(context, 'announcement.full')
        obj = models.Announcement.objects.create(content=content,
                                                 time=context.time)
        self = cls(context, obj)
        new = self._json_all
        for subscriber in self.subscribers:
            subscriber(None, new)
        return self

    @classmethod
    def get(cls, context, pk):
        try:
            return cls(context, models.Announcement.objects.get(pk=pk))
        except models.Announcement.DoesNotExist:
            raise NotFound('公告不存在')

    @classmethod
    def get_all(cls, context):
        return [cls(context, obj) for obj in models.Announcement.objects.all()]

    @classmethod
    def get_latest(cls, context):
        obj = models.Announcement.objects.first()
        if obj is None:
            raise NotFound('公告不存在')
        return cls(context, obj)

    def delete(self):
        User.test_permission(self._context, 'announcement.full')
        old = self._json_all
        self._obj.delete()
        self._obj = None
        for subscriber in self.subscribers:
            subscriber(old, None)

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
    def content(self):
        return self._obj.content

    @property
    def time(self):
        return self._obj.time
