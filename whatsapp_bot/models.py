from django.db import models

class Conversation(models.Model):
    phone_number = models.CharField(max_length=15)
    # messages = models.JSONField(null=True)

    def __str__(self):
        return self.phone_number
