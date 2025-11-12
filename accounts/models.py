from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random

class EmailOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(default=timezone.now)
    purpose = models.CharField(max_length=20, choices=[('register', 'register'), ('reset', 'reset')])

    def __str__(self):
        return f'{self.email} - {self.purpose}'

    @staticmethod
    def generate_otp():
        return f'{random.randint(100000, 999999)}'
