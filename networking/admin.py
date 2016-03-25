from django.contrib import admin

from .models import *


class DeviceInline(admin.TabularInline):
    model = Device


class SessionAdmin(admin.ModelAdmin):
    model = Session
    inlines = [
        DeviceInline,
    ]


admin.site.register(Session, SessionAdmin)
