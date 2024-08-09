# whatsapp_bot/urls.py
from django.urls import path

from .views import WebhookView, FlowView

urlpatterns = [
    path('webhook/', WebhookView.as_view(), name='webhook'),
    path('flow/', FlowView.as_view(), name='flow_endpoint'),
]
