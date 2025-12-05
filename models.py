from django.db import models
from django.contrib.auth.models import User
from django.core.serializers.json import DjangoJSONEncoder
import json

class GoogleCredentials(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    credentials = models.JSONField(encoder=DjangoJSONEncoder) # stores token/refresh/expiry, etc.
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} credentials"