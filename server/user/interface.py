import base64
import OpenSSL
from hashlib import sha256
from uuid import uuid4

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, EmailValidator

from server.exceptions import Error, NotFound, WrongArguments, WrongFormat
import server  # trigger support
from . import models


class LoginRequired(Error):
    code = 'login_required'
    message = '请先登录'


class PermissionRequired(Error):
    code = 'permission_required'
    message = '权限不足'


class ProfileRequired(Error):
    code = 'profile_required'
    message = '请完善个人信息'


def group_validator(group):
    if group not in User.groups:
        raise ValidationError('用户组不存在')


class User:
    json_fields = ('pk', 'is_staff', 'group', 'profile_ok',
                   'display_name', 'nickname', 'name', 'sno', 'tel',
                   'email', 'gender', 'qq', 'website', 'school',
                   'grade', 'major', 'campus', 'aff', 'token', 'token_short', 'code',
                   'suspicious_reason')
    update_fields = ('group', 'nickname', 'name', 'sno', 'tel', 'email',
                     'gender', 'qq', 'website', 'school', 'grade', 'major', 'campus',
                     'aff', 'suspicious_reason')
    groups = {
        'noscore': '不计分',
        'ustc': '中国科学技术大学',
        'zju': '浙江大学',
        'jlu': '吉林大学',
        'nuaa': '南京航空航天大学',
        'neu': '东北大学',
        'sysu': '中山大学',
        'xidian': '西安电子科技大学',
        'hit': '哈尔滨工业大学',
        'fdu': '复旦大学',
        'tongji': '同济大学',
        'gdou': '广东海洋大学',
        'sustech': '南方科技大学',
        'xmut': '厦门理工学院',
        'shu': '上海大学',
        'nyist': '南阳理工学院',
        'sjtu': '上海交通大学',
        'other': '其他选手',
        'suspicious': '待审核',
        'banned': '已封禁',
    }
    # XXX:
    # 以斜杠开头，然后接用斜杠隔开的 N 个字段，然后接斜杠和数字 K，表示 N 选 K。
    # K=0 和不放进列表中，在后端检查的逻辑上效果是相同的，都表示这些字段不需要填写，但在前端展示上是有区别的。
    # 如果不放进列表中，填写个人信息的前端页面是完全不会出现这个字段的。
    # 如果放进列表中，但 K=0，前端页面上就会出现相应的非必填字段。
    # 对于每个斜杠开头的项目，前端会出现一条提示信息，说明相应的规则，所以如果有多个非必填字段，应该合在一起写，例如 /name/sno/0，而不要写成两项，例如 /name/0 和 /sno/0。
    # TODO: 不要把信息这样扭曲地编码进字符串，而是明确分成三种情况：必填字段集合，选填字段集合（K=0 的部分），高级规则（K>0 的部分），用 json object 表示。
    profile_required = {
        'noscore': ['nickname'],
        'ustc': ['nickname', 'name', 'sno', 'tel', 'email'],
        'zju': ['nickname', 'name', 'sno', 'qq', 'major'],
        'jlu': ['nickname', 'name', 'sno', 'major'],
        'nuaa': ['nickname', 'name', 'sno', 'qq'],
        'neu': ['nickname', 'name', 'sno', 'school', 'major', 'qq'],
        'sysu': ['nickname', 'name', 'sno', 'school', 'major', 'qq'],
        'xidian': ['nickname', 'name', 'sno', 'qq', 'major'],
        'hit': ['nickname', 'name', 'sno', 'campus', 'school', 'qq'],
        'fdu': ['nickname', 'name', 'sno', 'school', 'major'],
        'tongji': ['nickname', 'name', 'sno', 'major'],
        'gdou': ['nickname', 'name', 'sno', 'school', 'campus', 'major', 'qq'],
        'sustech': ['nickname', 'name', 'sno'],
        'xmut': ['nickname', 'name', 'sno', 'school', 'campus', 'major', 'qq'],
        'shu': ['nickname'],
        'nyist': ['nickname', 'name', 'sno', 'school', 'major', 'qq'],
        'sjtu': ['nickname', 'name', 'sno'],
        'other': ['nickname'],
        'suspicious': ['nickname'],
        'banned': ['nickname'],
    }
    no_board_groups = ['noscore', 'other', 'suspicious', 'banned']
    no_code_groups = ['noscore', 'other', 'suspicious', 'banned']
    no_score_groups = ['noscore', 'suspicious', 'banned']
    subscribers = []
    _validators = {
        'group': group_validator,
        'nickname': RegexValidator(r'^.{1,30}$', '昵称应为 1～30 个字符'),
        'name': RegexValidator(r'^.{2,30}$', '姓名应为 2～30 个字符'),
        'sno': RegexValidator(r'^[a-zA-Z0-9]{4,30}$', '学号格式错误'),
        'tel': RegexValidator(r'^.{5,20}$', '电话格式错误'),
        'email': EmailValidator('邮箱格式错误'),
        'gender': RegexValidator(r'^(female|male|other)$',
                                 '性别应为 female，male，other 之一'),
        # QQ 号码可能是邮箱的形式，或许还有别的形式，所以用比较宽松的规则
        'qq': RegexValidator(r'^.{5,50}$', 'QQ 号码格式错误'),
        'website': RegexValidator(r'^.{1,300}$', '个人主页/博客格式错误'),
        'school': RegexValidator(r'^.{1,30}$', '学院格式错误'),
        'grade': RegexValidator(r'^.{1,10}$', '年级格式错误'),
        'major': RegexValidator(r'^.{1,15}$', '专业格式错误'),
        'campus': RegexValidator(r'^.{1,15}$', '校区格式错误'),
        'aff': RegexValidator(r'^.{1,100}$', '了解比赛的渠道格式错误'),
        'suspicious_reason': None,
    }
    _private_key = OpenSSL.crypto.load_privatekey(
        OpenSSL.crypto.FILETYPE_PEM, settings.PRIVATE_KEY)

    def __init__(self, context, obj: models.User):
        self._context = context
        self._obj = obj

    @classmethod
    def test_authenticated(cls, context):
        if context.elevated:
            return
        if not context.user.is_authenticated:
            raise LoginRequired()

    @classmethod
    def test_permission(cls, context, *permissions):
        if context.elevated:
            return
        for permission in permissions:
            if context.has_perm(permission):
                return
        raise PermissionRequired()

    @classmethod
    def test_profile(cls, context):
        if context.elevated:
            return
        if not cls.get(context, context.user.pk).profile_ok:
            raise ProfileRequired()

    @classmethod
    def create(cls, context, group, user=None, **kwargs):
        User.test_permission(context)
        context = context.copy(elevated=False)
        if user is None:
            user = get_user_model().objects.create_user(str(uuid4()))
        self = cls(context, models.User(user=user.pk))
        pk = str(user.pk)
        sig = base64.b64encode(OpenSSL.crypto.sign(
            self._private_key, pk.encode(), 'sha256')).decode()
        self._obj.token = pk + ':' + sig
        try:
            server.trigger.interface.Trigger.test_can_update_profile(context)
        except server.trigger.interface.TriggerIsOff:
            kwargs['nickname'] = "选手"
        self._update(group=group, **kwargs)
        new = self._json_all
        for subscriber in self.subscribers:
            subscriber(None, new)
        return self

    @classmethod
    def get(cls, context, pk):
        if pk is None:
            raise WrongArguments()
        try:
            return cls(context, models.User.objects.get(user=pk))
        except models.User.DoesNotExist:
            raise NotFound('用户不存在')

    @classmethod
    def get_all(cls, context):
        return [cls(context, i) for i in models.User.objects.order_by('pk')]

    @classmethod
    def get_all_for_board(cls, context):
        has_special_perm = False
        for perm in models.User._meta.permissions:
            if context.has_perm(f'user.{perm}'):
                has_special_perm = True
                break
        if has_special_perm:
            return {u.pk: u.json_without_profile_ok for u in cls.get_all(context)}
        else:
            return {u.pk: {'display_name': u.display_name} for u in cls.get_all(context)}

    @classmethod
    def get_public_data(cls, context):
        def f(o):
            o['display_name'] = o['nickname'] or ''
            del o['nickname']
            return o
        return list(map(f,
            models.User.objects
            .order_by('id')
            .values('id', 'group', 'nickname')
        ))

    def update(self, **kwargs):
        try:
            server.trigger.interface.Trigger.test_can_update_profile(self._context)
        except server.trigger.interface.TriggerIsOff:
            User.test_permission(self._context, 'user.full')
        if ('group' in kwargs and kwargs['group'] != self.group) or \
           ('suspicious_reason' in kwargs and kwargs['suspicious_reason'] != self.suspicious_reason):
            User.test_permission(self._context, 'user.full')
        if self._context.user.pk != self.pk:
            User.test_permission(self._context, 'user.full')
        old = self._json_all
        self._update(**kwargs)
        new = self._json_all
        for subscriber in self.subscribers:
            subscriber(old, new)

    def _update(self, **kwargs):
        for k, v in kwargs.items():
            if k in {'group', 'nickname', 'name', 'sno', 'tel', 'email',
                     'gender', 'qq', 'website', 'school', 'grade', 'major', 'campus',
                     'aff', 'suspicious_reason'}:
                v = v or None
                try:
                    v is None or (self._validators[k] and self._validators[k](v))
                except ValidationError as e:
                    raise WrongFormat(e.message)
                setattr(self._obj, k, v)
            else:
                raise WrongArguments()
        self._obj.save()
        self._obj.refresh_from_db()
        models.UserLog.objects.create(
            context_user=self._context.user.id,
            context_time=self._context.time,
            context_elevated=self._context.elevated,
            **{k: getattr(self._obj, k) for k in {
                'user', 'group', 'nickname', 'name', 'sno', 'tel',
                'email', 'gender', 'qq', 'website', 'school', 'grade', 'major', 'campus',
                'aff', 'token', 'suspicious_reason'
            }},
        )

    def delete(self):
        User.test_permission(self._context, 'user.full')
        old = self._json_all
        self.user.delete()
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
    def json_without_profile_ok(self):
        result = {}
        for i in self.json_fields:
            if i == 'profile_ok':
                continue
            try:
                result[i] = getattr(self, i)
            except PermissionRequired:
                pass
        return result

    @property
    def _json_all(self):
        return type(self)(self._context.copy(elevated=True), self._obj).json

    @property
    def profile_ok(self):
        if self.group == 'banned':
            return False
        try:
            server.trigger.interface.Trigger.test_can_update_profile(self._context)
        except server.trigger.interface.TriggerIsOff:
            return True
        for field in self.profile_required[self.group]:
            if field.startswith('/'):
                # 这种记法表示 N 选 K
                *fields, minimum = field[1:].split('/')
                count = sum(getattr(self, i) is not None for i in fields)
                if count < int(minimum):
                    return False
            else:
                # 普通的必填字段
                if getattr(self, field) is None:
                    return False
        return True

    @property
    def pk(self):
        return self._obj.user

    @property
    def user(self):
        return get_user_model().objects.get(pk=self.pk)

    @property
    def is_staff(self):
        # XXX: 允许随便获取此项信息会导致性能问题
        if self._context.user.pk != self.pk:
            User.test_permission(self._context)
        return self.user.is_staff

    @property
    def group(self):
        return self._obj.group

    @property
    def display_name(self):
        return self.nickname or ''

    @property
    def nickname(self):
        return self._obj.nickname

    @property
    def name(self):
        if self._context.user.pk != self.pk:
            User.test_permission(self._context, 'user.full',
                                 'user.view', f'user.view_{self.group}')
        return self._obj.name

    @property
    def sno(self):
        if self._context.user.pk != self.pk:
            User.test_permission(self._context, 'user.full',
                                 'user.view', f'user.view_{self.group}')
        return self._obj.sno

    @property
    def tel(self):
        if self._context.user.pk != self.pk:
            User.test_permission(self._context, 'user.full',
                                 'user.view', f'user.view_{self.group}')
        return self._obj.tel

    @property
    def email(self):
        if self._context.user.pk != self.pk:
            User.test_permission(self._context, 'user.full',
                                 'user.view', f'user.view_{self.group}')
        return self._obj.email

    @property
    def gender(self):
        if self._context.user.pk != self.pk:
            User.test_permission(self._context, 'user.full',
                                 'user.view', f'user.view_{self.group}')
        return self._obj.gender

    @property
    def major(self):
        if self._context.user.pk != self.pk:
            User.test_permission(self._context, 'user.full',
                                 'user.view', f'user.view_{self.group}')
        return self._obj.major

    @property
    def campus(self):
        if self._context.user.pk != self.pk:
            User.test_permission(self._context, 'user.full',
                                 'user.view', f'user.view_{self.group}')
        return self._obj.campus

    @property
    def qq(self):
        if self._context.user.pk != self.pk:
            User.test_permission(self._context, 'user.full',
                                 'user.view', f'user.view_{self.group}')
        return self._obj.qq

    @property
    def website(self):
        if self._context.user.pk != self.pk:
            User.test_permission(self._context, 'user.full',
                                 'user.view', f'user.view_{self.group}')
        return self._obj.website

    @property
    def school(self):
        if self._context.user.pk != self.pk:
            User.test_permission(self._context, 'user.full',
                                 'user.view', f'user.view_{self.group}')
        return self._obj.school

    @property
    def grade(self):
        if self._context.user.pk != self.pk:
            User.test_permission(self._context, 'user.full',
                                 'user.view', f'user.view_{self.group}')
        return self._obj.grade

    @property
    def aff(self):
        if self._context.user.pk != self.pk:
            User.test_permission(self._context, 'user.full',
                                 'user.view', f'user.view_{self.group}')
        return self._obj.aff

    @property
    def token(self):
        if self._context.user.pk != self.pk:
            User.test_permission(self._context)
        return self._obj.token

    @property
    def token_short(self):
        if self._context.user.pk != self.pk:
            User.test_permission(self._context, 'user.full',
                                 'user.view', f'user.view_{self.group}')
        token = self._obj.token
        return token[: token.find(':') + 11] + '...'

    @property
    def code(self):
        if self._context.user.pk != self.pk:
            User.test_permission(self._context, 'user.full',
                                 'user.view', f'user.view_{self.group}')
        if self.group in self.no_code_groups:
            return None
        token = self._obj.token
        return f'{self.pk}-{int(sha256(token.encode()).hexdigest(), 16)%10000:04}'

    @property
    def suspicious_reason(self):
        if self._context.user.pk != self.pk:
            User.test_permission(self._context, 'user.full', 'user.view')
        return self._obj.suspicious_reason
