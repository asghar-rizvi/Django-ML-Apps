from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class userInfo(models.Model):
    user = models.ForeignKey(User, related_name ='User', on_delete=models.CASCADE)
    category = models.CharField(max_length=50)
