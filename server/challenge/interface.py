import json

from server.terms.interface import Terms
from server.trigger.interface import Trigger
from server.user.interface import User, PermissionRequired
from server.context import Context
from server.exceptions import NotFound, WrongArguments
from . import models


class Challenge:
    json_fields = ('pk', 'score', 'enabled', 'name', 'category',
                   'detail', 'url', 'prompt', 'index', 'flags')
    update_fields = ('enabled', 'name', 'category', 'detail', 'url',
                     'prompt', 'index', 'flags')
    subscribers = []

    def __init__(self, context, obj: models.Challenge):
        self._context = context
        self._obj = obj

    @classmethod
    def create(cls, context, **kwargs):
        User.test_permission(context, 'challenge.full')
        self = cls(context, models.Challenge())
        flags = kwargs.pop('flags')
        self._update(**kwargs)
        self._update(flags=flags)
        new = self._json_all
        for subscriber in self.subscribers:
            subscriber(None, new)
        return self

    @classmethod
    def get(cls, context, pk):
        queryset = models.Challenge.objects.all()
        try:
            User.test_permission(context, 'challenge.full', 'challenge.view')
        except PermissionRequired:
            User.test_authenticated(context)
            Terms.test_agreed_enabled(context)
            User.test_profile(context)
            Trigger.test_can_view_challenges(context)
            queryset = queryset.filter(enabled=True)
        try:
            return cls(context, queryset.get(pk=pk))
        except models.Challenge.DoesNotExist:
            raise NotFound('题目不存在')

    @classmethod
    def get_all(cls, context):
        User.test_permission(context, 'challenge.full', 'challenge.view')
        return [cls(context, obj) for obj in models.Challenge.objects.all()]

    @classmethod
    def get_enabled(cls, context):
        User.test_authenticated(context)
        Terms.test_agreed_enabled(context)
        User.test_profile(context)
        try:
            User.test_permission(context, 'challenge.full', 'challenge.view')
        except PermissionRequired:
            Trigger.test_can_view_challenges(context)
        queryset = models.Challenge.objects.filter(enabled=True)
        return [cls(context, obj) for obj in queryset]

    def check_flag_with_violations(self, text):
        flags = [{'index': i, **f} for i, f in enumerate(self.flags)]
        matches = []
        for i, flag in enumerate(json.loads(self._obj.flags)):
            if flag['type'] == 'text':
                if text == flag['flag']:
                    matches.append(flags[i])
            elif flag['type'] == 'expr':
                if models.ExprFlag.objects.filter(
                    expr=flag['flag'],
                    user=self._context.user.pk,
                    flag=text,
                ).exists():
                    matches.append(flags[i])
        if matches:
            return matches, []
        violations = []
        for i, flag in enumerate(json.loads(self._obj.flags)):
            if flag['type'] == 'expr':
                for match in models.ExprFlag.objects.filter(expr=flag['flag'],
                                                            flag=text):
                    violations.append((flags[i], match.user))
        return [], violations

    def update(self, **kwargs):
        User.test_permission(self._context, 'challenge.full')
        old = self._json_all
        self._update(**kwargs)
        new = self._json_all
        for subscriber in self.subscribers:
            subscriber(old, new)

    def _update(self, **kwargs):
        for k, v in kwargs.items():
            if k in {'name', 'category', 'url', 'prompt'}:
                v = v or None
                setattr(self._obj, k, v)
            elif k in {'enabled', 'detail', 'index'}:
                setattr(self._obj, k, v)
            elif k == 'flags':
                flags = [{
                    'name': str(flag['name']),
                    'score': int(flag['score']),
                    'type': str(flag['type']),
                    'flag': str(flag['flag']),
                } for flag in v]
                setattr(self._obj, k, json.dumps(flags))
                for flag in flags:
                    if flag['type'] != 'expr':
                        continue
                    self._add_expr(flag['flag'])
                self._obj.expr_set.all().delete()
                for i, flag in enumerate(flags):
                    if flag['type'] != 'expr':
                        continue
                    self._obj.expr_set.create(flag_index=i, expr=flag['flag'])
            else:
                raise WrongArguments()
        self._obj.save()
        self._obj.refresh_from_db()

    def delete(self):
        User.test_permission(self._context, 'challenge.full')
        old = self._json_all
        self._obj.expr_set.all().delete()
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
    def score(self):
        return sum(flag['score'] for flag in self.flags)

    @property
    def enabled(self):
        return self._obj.enabled

    @property
    def name(self):
        return self._obj.name

    @property
    def category(self):
        return self._obj.category

    @property
    def detail(self):
        return self._obj.detail

    @property
    def url(self):
        return self._obj.url

    @property
    def prompt(self):
        return self._obj.prompt

    @property
    def index(self):
        return self._obj.index

    @property
    def flags(self):
        flags = json.loads(self._obj.flags)
        try:
            User.test_permission(self._context, 'challenge.full',
                                 'challenge.view')
            return flags
        except PermissionRequired:
            return [{
                'name': flag['name'],
                'score': flag['score'],
            } for flag in flags]

    @classmethod
    def regen_all(cls, context):
        """重算所有缓存，只有通过命令行提权后才能调用"""
        User.test_permission(context)
        models.User.objects.all().delete()
        models.Expr.objects.all().delete()
        models.ExprFlag.objects.all().delete()
        for challenge in cls.get_all(context):
            for i, flag in enumerate(challenge.flags):
                if flag['type'] != 'expr':
                    continue
                challenge._obj.expr_set.create(flag_index=i, expr=flag['flag'])
        for user in User.get_all(context):
            if not user.token:
                continue
            cls._add_user(user.pk)
            models.User.objects.create(user=user.pk)

    @classmethod
    def _add_expr(cls, expr):
        from .expr_flags import expr_flag
        if models.Expr.objects.filter(expr=expr).exists():
            return False
        for user_obj in models.User.objects.all():
            if models.ExprFlag.objects.filter(
                expr=expr,
                user=user_obj.user,
            ).exists():
                continue
            token = User.get(Context(elevated=True), user_obj.user).token
            models.ExprFlag.objects.create(
                expr=expr,
                user=user_obj.user,
                flag=expr_flag(expr, token),
            )
        return True

    @classmethod
    def _add_user(cls, user):
        from .expr_flags import expr_flag
        if models.User.objects.filter(user=user).exists():
            return False
        token = User.get(Context(elevated=True), user).token
        for expr_obj in models.Expr.objects.values('expr').distinct():
            if models.ExprFlag.objects.filter(
                expr=expr_obj['expr'],
                user=user,
            ).exists():
                continue
            models.ExprFlag.objects.create(
                expr=expr_obj['expr'],
                user=user,
                flag=expr_flag(expr_obj['expr'], token),
            )
        return True

    @classmethod
    def _user_event(cls, old, new):
        old_token = old and old.get('token')
        new_token = new and new.get('token')
        if new_token and new_token != old_token:
            if cls._add_user(new['pk']):
                models.User.objects.create(user=new['pk'])

    @classmethod
    def app_ready(cls):
        User.subscribers.append(cls._user_event)
