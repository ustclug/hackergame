from django.contrib import admin

from user.models import User, Term


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'last_name', 'phone_number')
    list_filter = ('group',)


admin.site.register(User, UserAdmin)
admin.site.register(Term)
