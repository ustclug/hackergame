from django.contrib import admin

from .models import Device, Token

admin.site.register((Device, Token))
