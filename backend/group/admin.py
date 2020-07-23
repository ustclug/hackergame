from django.contrib import admin
from django.utils.html import format_html

from group.models import Group, Application


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('test',)
    search_fields = ('name',)
    filter_horizontal = ('users',)

    def test(self, obj):
        return format_html('<span style="color: #FF0000">{}</span>',
                           obj.id)


admin.site.register(Application)
