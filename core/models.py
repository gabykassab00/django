from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
class Users(AbstractUser):
    username=None
    email = models.CharField(max_length=255,unique=True)
    password = models.CharField(max_length=255)
    
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=[]
    
    
class Usertoken(models.Model):
    user_id = models.IntegerField()
    token=models.CharField(max_length=255)
    created_at=models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField()


class Reset(models.Model):
    email = models.CharField(max_length=255)
    token=models.CharField(max_length=255,unique=True)
    
    
class Team(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='teams'
    )
    date = models.DateField()
    game = models.CharField(max_length=255)
    ball_control = models.FloatField()
    distance_covered = models.FloatField()
    average_speed = models.FloatField()
    total_passes = models.PositiveIntegerField()
    
    
    def __str__(self):
        return f"Team data for {self.user.email} on {self.date}"
    
