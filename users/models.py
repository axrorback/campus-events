from django.db import models
from django.contrib.auth.models import User

class ExternalUserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='external_profile')
    external_user_id = models.CharField(max_length=64, unique=True)  # API dagi userId
    preferred_name = models.CharField(max_length=255, blank=True)
    email = models.EmailField(blank=True)
    mobile = models.CharField(max_length=32, blank=True)
    usertype = models.CharField(max_length=64, blank=True)
    emp_or_std_id = models.CharField(max_length=64, blank=True)
    role = models.CharField(max_length=128, blank=True)
    role_short = models.CharField(max_length=64, blank=True)
    role_id = models.CharField(max_length=64, blank=True)
    photo_local = models.ImageField(upload_to='profiles/', blank=True, null=True)  # yuklab olingan rasm
    photo_path = models.CharField(max_length=255, blank=True, null=True)  # << YANGI

    def __str__(self):
        return self.user.username
