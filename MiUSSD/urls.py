from django.urls import path
from .views import ussd_view

urlpatterns = [
    path('', ussd_view, name='ussd_view'),
]
