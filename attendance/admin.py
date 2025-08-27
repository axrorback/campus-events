from django.contrib import admin
from .models import Registration

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('id','event','user','attended','created_at','attended_at')
    list_filter = ('attended','event')
    search_fields = ('user__username','user__first_name','event__title')
