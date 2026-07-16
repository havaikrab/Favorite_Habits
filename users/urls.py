from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from . import views
from .apps import UsersConfig

app_name = UsersConfig.name

router = DefaultRouter()
router.register("", views.CustomUserViewSet)

urlpatterns: list = [
    path("register/", views.CustomUserRegisterAPIView.as_view(), name="register"),
    path("login/", TokenObtainPairView.as_view(), name="login"),
    path("token_refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("webhook/", views.TGChatWebhookAPIView.as_view(), name="webhook"),
]
urlpatterns += router.urls
