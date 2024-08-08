from django.db import models
from django.conf import settings
import json

class ResponseTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    template = models.JSONField()

    def render(self, context):
        """
        Render the template with the provided context.
        """
        template_str = json.dumps(self.template)
        for key, value in context.items():
            template_str = template_str.replace(f'{{{{ {key} }}}}', str(value))
        return json.loads(template_str)

    def __str__(self):
        return self.name


class UserInteraction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    phone_number = models.CharField(max_length=15)
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Interaction with {self.phone_number} at {self.timestamp}"