from django.contrib import admin

from django.contrib.auth.admin import UserAdmin as BaseDjangoUserAdmin
from django.contrib.auth.models import User as DjangoUser

from server.announcement.models import Announcement
from server.challenge.models import Challenge
from server.submission.models import Submission
from server.terms.models import Terms
from server.trigger.models import Trigger
from server.user.models import User
from .models import Page, Account, Code, AccountLog, SpecialProfileUsedRecord, Qa, Credits

admin.site.register([Page, Account, Code, Qa, Credits, SpecialProfileUsedRecord])


class PermissionListFilter(admin.SimpleListFilter):
    title = '权限'
    parameter_name = 'permission'

    def lookups(self, request, model_admin):
        return [
            ("has_permission", "有非空「用户权限」的用户"),
        ]
    
    def queryset(self, request, queryset):
        if self.value() == "has_permission":
            return queryset.filter(user_permissions__isnull=False)


class DjangoUserAdmin(BaseDjangoUserAdmin):
    def __init__(self, model, admin_site) -> None:
        super().__init__(model, admin_site)
        self.list_filter += (PermissionListFilter, )


admin.site.unregister(DjangoUser)
admin.site.register(DjangoUser, DjangoUserAdmin)

# XXX: Hack here
# I also replaced template `admin/index.html`, so that these entries
# show up on the admin page, while low-level models still kept
# inaccessible.
@admin.register(Announcement, Challenge, Submission, Terms, Trigger, User)
class FakeAdmin(admin.ModelAdmin):
    def get_model_perms(self, request):
        return {None: True}

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def has_view_permission(self, request, obj=None):
        return False


@admin.register(AccountLog)
class AccountLogAdmin(admin.ModelAdmin):
    search_fields = ["account__pk", "contents"]
