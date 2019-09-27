from django.db import models


class Page(models.Model):
    title = models.TextField(default='Hackergame')
    description = models.TextField(blank=True)
    keywords = models.TextField(blank=True, default='Hackergame,CTF')
    content = models.TextField(blank=True, default='<h1>Hackergame</h1>',
                               help_text='会被放入 <code>div</code> 的 HTML')

    def __str__(self):
        return self.title

    @classmethod
    def get(cls):
        return cls.objects.get_or_create()[0]
