from django.contrib import admin

from server.announcement.models import Announcement
from server.challenge.models import Challenge
from server.submission.models import Submission
from server.terms.models import Terms
from server.trigger.models import Trigger
from server.user.models import User
from .models import Page, Account, Code, UstcSnos, UstcEligible, Qa

admin.site.register([Page, Account, Code, UstcSnos, UstcEligible, Qa])


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
