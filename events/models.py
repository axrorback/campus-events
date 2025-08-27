from django.db import models
from django.contrib.auth.models import User
import uuid

class Event(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    location = models.CharField(max_length=255)
    room = models.CharField(max_length=64, blank=True)
    published_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='published_events')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def registered_count(self):
        return self.registrations.count()

    def attended_count(self):
        return self.registrations.filter(attended=True).count()

    def __str__(self):
        return self.title
