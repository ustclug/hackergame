from django.db import models
from django.utils import timezone

from challenge.models import Challenge


class Announcement(models.Model):
    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, null=True, blank=True,
                                  help_text='为空则为一般公告')
    content = models.TextField()
    created_time = models.DateTimeField(default=timezone.now, editable=False)
    updated_time = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.challenge:
            challenge = self.challenge.name
        else:
            challenge = 'General'
        return f'{self.id}-{challenge}'

    class Meta:
        default_permissions = []
