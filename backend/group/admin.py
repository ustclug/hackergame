from django.contrib import admin

from group.models import Group, Application


@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    search_fields = ('name',)
    readonly_fields = ('users',)
    fieldsets = (
        (None, {
            'fields': ('name', 'admin', 'users'),
        }),
        ('Rules', {
            'fields': (
                'rule_has_phone_number',
                'rule_has_email',
                'rule_email_suffix',
                'rule_has_name',
                'rule_must_be_verified_by_admin',
                'apply_hint',
            ),
        }),
        ('Verification', {
            'fields': ('verified', 'verify_message')
        })
    )


admin.site.register(Application)
