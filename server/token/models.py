from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Token(models.Model):
    user = models.OneToOneField(User, models.CASCADE, primary_key=True)
    token = models.TextField(db_index=True)

    def __str__(self):
        return self.token
