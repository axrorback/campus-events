from django.contrib import admin
from .models import Event

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title','start_at','end_at','location','room','is_active','published_by','created_at')
    list_filter = ('is_active','location')
    search_fields = ('title','description','location','room')
