from django.db import models
from django.contrib.auth.models import User
from events.models import Event
import uuid

class Registration(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registrations')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    qr_image = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    invitation_image = models.ImageField(upload_to='invites/', blank=True, null=True)  # maxsus taklifnoma rasm
    created_at = models.DateTimeField(auto_now_add=True)
    attended = models.BooleanField(default=False)
    attended_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'event')


class AttendanceLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    scanned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-scanned_at']  # eng yangi birinchi chiqadi
