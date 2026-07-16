from django.urls import path

from . import views
from .apps import UsersConfig

app_name = UsersConfig.name

urlpatterns = [
    path("register/", views.CustomUserRegisterAPIView.as_view(), name="register"),
    path("webhook/", views.TGChatWebhookAPIView.as_view(), name="webhook"),
]
