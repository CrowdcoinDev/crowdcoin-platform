from django.db import models
from django.conf import settings
import importlib

class Campaign(models.Model):
    name = models.CharField(max_length=100)
    ussd_number = models.CharField(max_length=15, unique=True)
    starting_node = models.ForeignKey('Node', related_name='campaign_starting_node', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

class Node(models.Model):
    name = models.CharField(max_length=100)
    campaign = models.ForeignKey(Campaign, related_name='nodes', on_delete=models.CASCADE)
    text_response = models.TextField(null=True, blank=True)
    link_response = models.URLField(null=True, blank=True)
    function_response = models.CharField(max_length=255, null=True, blank=True)
    script_response = models.TextField(null=True, blank=True)  # New field for script-like functions
    session_end = models.BooleanField(default=False)  # New field to indicate if session should end after this node

    def __str__(self):
        return self.name

    def get_response(self, request, user_response):
        node_response = self.responses.filter(user_response=user_response).first()
        if node_response and node_response.next_node:
            return node_response.next_node.get_response(request, user_response)
        if self.text_response:
            return self.text_response
        elif self.link_response:
            return self.fetch_link_response(user_response)
        elif self.function_response:
            return self.execute_function_response(request, user_response)
        elif self.script_response:
            return self.execute_script_response(request, user_response)
        return "Invalid response configuration."

    def fetch_link_response(self, user_response):
        # Implement the logic to fetch the response from a link
        pass

    def execute_function_response(self, request, user_response):
        module_name, function_name = self.function_response.rsplit('.', 1)
        module = importlib.import_module(module_name)
        function = getattr(module, function_name)
        return function(request, user_response)

    def execute_script_response(self, request, user_response):
        # Implement the logic to execute the script-like function
        local_vars = {}
        exec(self.script_response, {}, local_vars)
        return local_vars['response'](request, user_response)

class NodeResponse(models.Model):
    node = models.ForeignKey(Node, related_name='responses', on_delete=models.CASCADE)
    user_response = models.CharField(max_length=255)
    next_node = models.ForeignKey(Node, related_name='incoming_responses', on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.node.name} - {self.user_response} -> {self.next_node.name}"

class Interaction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    node = models.ForeignKey(Node, on_delete=models.CASCADE)
    response = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)
    session_data = models.JSONField(null=True, blank=True)  # To store session data

    def __str__(self):
        return f"{self.user} - {self.node} - {self.response}"
