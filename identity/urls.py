from django.urls import path
from .views import identify

urlpatterns = [
    path('identify', identify),  # POST endpoint
]
