from typing import Any, Sequence

from mypy.util import json_loads
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from .models import CustomUser
from .permissions import IsOwner
from .serializers import CustomUserRegisterSerializer, CustomUserSerializer
from .services import tg_message_handler


class CustomUserRegisterAPIView(CreateAPIView):
    """Контроллер регистрации нового пользователя"""

    serializer_class = CustomUserRegisterSerializer
    permission_classes = [AllowAny]


class TGChatWebhookAPIView(APIView):
    """Контроллер активации телеграм-чата с пользователем"""

    authentication_classes = []
    permission_classes = []

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Получение из тела запроса ID чата с пользователем и сохранение его в БД"""

        data = json_loads(request.body)
        tg_message_handler(data)
        return Response(status=status.HTTP_200_OK)


class CustomUserViewSet(ModelViewSet):
    """Вьюсет для модели пользователя"""

    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    http_method_names = ["get", "put", "patch", "delete"]

    def get_permissions(self) -> Sequence:
        """Указание необходимых разрешений для соответствующих действий контроллера"""

        if self.action in ["destroy", "update", "partial_update"]:
            self.permission_classes = [IsAuthenticated & IsOwner]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()
