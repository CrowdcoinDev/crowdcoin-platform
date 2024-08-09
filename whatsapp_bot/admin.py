from django.contrib import admin
from .models import *

@admin.register(UserInteraction)
class UserInteractionAdmin(admin.ModelAdmin):
    list_display = ['phone_number','user']
    search_fields = ['phone_number','user','messages']

admin.site.register(ResponseTemplate)
admin.site.register(Flow)
admin.site.register(FlowStep)