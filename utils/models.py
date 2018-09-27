from django.utils.functional import cached_property


class DictMixin:
    @classmethod
    def keys(cls):
        for field in cls._meta.get_fields():
            if field.is_relation:
                if field.one_to_many:
                    continue
                elif field.many_to_many:
                    raise NotImplementedError
                else:
                    yield field.name + '_id'
            else:
                yield field.name
        for attr in dir(cls):
            if isinstance(getattr(cls, attr), (property, cached_property)):
                yield attr

    def __getitem__(self, item):
        return getattr(self, item)


class NameMixin:
    def __str__(self):
        return self.name


class UpdateCacheMixin:
    def update_cache(self):
        raise NotImplementedError

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.update_cache()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.update_cache()
