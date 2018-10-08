from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.db import models
from django.utils.timezone import now

from utils.cache import timeout_at

User = get_user_model()


class Terms(models.Model):
    name = models.TextField()
    content = models.TextField(blank=True, help_text='Will be put into a div as HTML.')
    begin = models.DateTimeField(default=now, db_index=True)
    replace = models.ManyToManyField('self', blank=True, related_name='replaced_by', symmetrical=False,
                                     help_text='When in effect, obsolete these.')
    agreed = models.ManyToManyField(User, blank=True)

    def __str__(self):
        if self.replaced_by.count():
            return f'{self.name} (obsolete)'
        else:
            return self.name

    @classmethod
    def current_terms(cls):
        key = 'terms__current_terms'
        cached = cache.get(key)
        if cached is None:
            time = now()
            cached = list(cls.objects.filter(~models.Q(replaced_by__begin__lte=time), begin__lte=time))
            next_time = cls.objects.filter(begin__gt=time).aggregate(models.Min('begin'))['begin__min']
            cache.set(key, cached, timeout_at(next_time))
        return cached

    def _clear_cache(**kwargs):
        _ = kwargs
        key = 'terms__current_terms'
        cache.delete(key)

    models.signals.post_save.connect(_clear_cache, sender='terms.Terms')
    models.signals.post_delete.connect(_clear_cache, sender='terms.Terms')

    @classmethod
    def agreed_all_terms(cls, user):
        current_terms = cls.current_terms()
        return user.terms_set.filter(pk__in=[terms.pk for terms in current_terms]).count() == len(current_terms)
