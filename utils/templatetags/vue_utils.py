from django import template

register = template.Library()


@register.filter(name='list')
def to_list(object_list):
    return [dict(o) for o in object_list]


@register.filter(name='dict')
def to_dict(object_list):
    return {o.pk: dict(o) for o in object_list}
