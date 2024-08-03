# backend/urls.py
# from django.urls import path
from django.conf.urls import  include, url

from .views import WebhookView

urlpatterns = [
    # path('webhook/', WebhookView.as_view(), name='webhook'),
    url(r'^webhook/$', view=WebhookView.as_view(), name='webhook'),
]
