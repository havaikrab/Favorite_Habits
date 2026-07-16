from typing import Any

from mypy.util import json_loads
from rest_framework import status
from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import CustomUserRegisterSerializer
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
