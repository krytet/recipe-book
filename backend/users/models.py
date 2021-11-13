from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models

User = get_user_model()


class Subscription(models.Model):
    respondent = models.ForeignKey(User, on_delete=models.CASCADE,
                                   related_name='subscription'
                                   )
    subscriptions = models.ForeignKey(User, on_delete=models.CASCADE,
                                      related_name='subscribers'
                                      )

    def __str__(self):
        return f"{self.respondent} подписался на {self.subscriptions}"
