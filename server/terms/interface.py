from typing import List, Callable

from server.user.interface import User, PermissionRequired
from server.exceptions import Error, WrongArguments, NotFound
from . import models


class TermsRequired(Error):
    code = 'terms_required'
    message = '请同意用户条款'


class Terms:
    json_fields = ('pk', 'name', 'content', 'enabled')
    update_fields = ('name', 'content', 'enabled')
    subscribers: List[Callable] = []

    def __init__(self, context, obj: models.Terms):
        self._context = context
        self._obj = obj

    @classmethod
    def test_agreed_enabled(cls, context):
        if context.elevated:
            return
        queryset = (
            models.Terms.objects
            .filter(enabled=True)
            .exclude(agreement__user=context.user.pk)
        )
        if queryset.exists():
            raise TermsRequired()

    @classmethod
    def get(cls, context, pk):
        try:
            return cls(context, models.Terms.objects.get(pk=pk))
        except models.Terms.DoesNotExist:
            raise NotFound()

    @classmethod
    def get_all(cls, context):
        return [cls(context, obj) for obj in models.Terms.objects.all()]

    @classmethod
    def get_enabled(cls, context):
        return [cls(context, obj) for obj in (
            models.Terms.objects
            .filter(enabled=True)
        )]

    @classmethod
    def create(cls, context, **kwargs):
        User.test_permission(context, 'terms.full')
        self = cls(context, models.Terms())
        self._update(**kwargs)
        new = self._json_all
        for subscriber in self.subscribers:
            subscriber(None, new)
        return self

    def agree(self, user):
        if self._context.user.pk != user:
            User.test_permission(self._context)
        models.Agreement.objects.get_or_create(user=user, terms=self._obj)

    def update(self, **kwargs):
        User.test_permission(self._context, 'terms.full')
        old = self._json_all
        self._update(**kwargs)
        new = self._json_all
        for subscriber in self.subscribers:
            subscriber(old, new)

    def _update(self, **kwargs):
        for k, v in kwargs.items():
            if k in {'name', 'content'}:
                v = v or None
                setattr(self._obj, k, v)
            elif k in {'enabled'}:
                setattr(self._obj, k, v)
            else:
                raise WrongArguments()
        self._obj.save()
        self._obj.refresh_from_db()

    def delete(self):
        User.test_permission(self._context, 'terms.full')
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
    def name(self):
        return self._obj.name

    @property
    def content(self):
        return self._obj.content

    @property
    def enabled(self):
        return self._obj.enabled
