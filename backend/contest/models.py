from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


class StageManager(models.Manager):
    def get(self):
        if self.get_queryset().count() == 0:
            raise ValidationError("Stage 表未被初始化")
        return self.get_queryset().all()[0]

    @classmethod
    def _now(cls):
        """便于测试 monkeypatch 这个方法"""
        return timezone.now()

    @property
    def current_status(self):
        """比赛的当前状态, 共有五种可能的情况"""
        cur_time = self._now()
        stage = self.get()
        pauses = Pause.objects.all()
        if cur_time < stage.start_time:
            return "not start"
        elif stage.end_time < cur_time < stage.practice_start_time:
            return "ended"
        elif stage.practice_start_time < cur_time:
            return "practice"
        for pause in pauses:
            if pause.start_time < cur_time < pause.end_time:
                return "paused"
        return "underway"


class Stage(models.Model):
    """比赛各阶段的时间点, 整个表只允许一行数据"""
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    practice_start_time = models.DateTimeField()

    objects = StageManager()

    def save(self, **kwargs):
        if not self.pk and Stage.objects.count():
            raise ValidationError("Stage table can only have one line.")
        super().save(**kwargs)

    class Meta:
        default_permissions = []


class Pause(models.Model):
    """表示比赛暂停的时段"""
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    note = models.TextField(blank=True)

    def save(self, **kwargs):
        stage = Stage.objects.get()
        if self.start_time < stage.start_time:
            raise ValidationError("Pause start time must be after contest start time.")
        if self.end_time > stage.end_time:
            raise ValidationError("Pause end time must be before contest end time.")
        super().save(**kwargs)

    class Meta:
        default_permissions = []
