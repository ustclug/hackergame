from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


from user.models import User, Term
# from user.utils import generate_uuid_and_token


@admin.register(User)
class UserAdmin(UserAdmin):
    fieldsets = (
        (None, {
            'fields': ('username', 'password', 'last_name', 'email', 'phone_number')
        }),
        ('Advanced', {
            'fields': ('term_agreed', 'groups', 'is_superuser', 'is_staff', 'token'),
        }),
    )
    list_display = ('username', 'email', 'last_name', 'phone_number')
    list_filter = ('groups',)
    readonly_fields = ('token',)


@admin.register(Term)
class TermAdmin(admin.ModelAdmin):
    readonly_fields = ('date_modified',)
    list_display = ('__str__', 'enabled')
