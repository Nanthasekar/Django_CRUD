from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.

class Blog(models.Model):
     # This model store entire config  values

    title = models.CharField(max_length=100, unique=True)
    message  = models.TextField(blank=True, null=True)
    username = models.CharField(max_length=100)
    created_by = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    modified_at = models.DateTimeField(auto_now=True, blank=True, null=True)
