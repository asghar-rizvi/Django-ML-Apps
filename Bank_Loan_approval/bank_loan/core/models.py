from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class predict_user(models.Model):
     user = models.ForeignKey(User, on_delete=models.CASCADE, null = True, blank = True)
     credit_card_score = models.FloatField()
     loan_Status = models.CharField(max_length=30)
     