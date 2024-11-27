from django.contrib import admin

from .models import Profile, Activity, Device, StandUp, Movement

admin.site.register(Profile)
admin.site.register(Activity)
admin.site.register(Device)
admin.site.register(StandUp)
admin.site.register(Movement)
