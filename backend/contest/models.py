from django.db import models
from django.utils import timezone


class StageManager(models.Manager):
    def get(self):
        return self.get_queryset().all()[0]

    @classmethod
    def now(cls):
        return timezone.now()

    @property
    def current_status(self):
        cur_time = self.now()
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
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    practice_start_time = models.DateTimeField()

    objects = StageManager()


# FIXME: 如何保证暂停在比赛进行的时间范围内?
class Pause(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    note = models.TextField(blank=True)
