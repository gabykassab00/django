from django.contrib.auth.models import AbstractUser
from django.db import models
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
