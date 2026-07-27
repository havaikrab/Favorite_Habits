from typing import Any, Sequence

from django.utils.decorators import method_decorator
from drf_spectacular.utils import OpenApiResponse, extend_schema, extend_schema_view
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


@method_decorator(
    name="post",
    decorator=extend_schema(
        summary="Регистрация нового пользователя",
        responses={
            200: OpenApiResponse(description="""
{"username": "test_user", "email": "test@user.py", "first_name": "Test", "last_name": "User",
"""),
            400: OpenApiResponse(description="""
- Не указано одно или несколько обязательных полей:
  "username", "email", "first_name", "last_name", "password", "password_confirm".
- Пароли не совпадают.
- Пользователь с таким "username" или "email" уже существует.
"""),
        },
    ),
)
class CustomUserRegisterAPIView(CreateAPIView):
    """Контроллер регистрации нового пользователя"""

    serializer_class = CustomUserRegisterSerializer
    permission_classes = [AllowAny]


@method_decorator(
    name="post",
    decorator=extend_schema(
        summary="Обработчик Telegram-вебхуков",
        description="""
Данный контроллер не предназначен для взаимодействия с пользователем.
На данном этапе разработки, контроллер предназначен для автоматического заполнения поля tg_chat_id
у объекта пользователя. После получения данного идентификатора телеграм-бот начнет отправлять пользователю уведомления
о наступлении запланированных событий.""",
        responses={
            200: OpenApiResponse(description='Возвращается "пустой" объект response.'),
        },
    ),
)
class TGChatWebhookAPIView(APIView):
    """Контроллер активации телеграм-чата с пользователем"""

    authentication_classes = []
    permission_classes = []

    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """Получение из тела запроса ID чата с пользователем и сохранение его в БД"""

        data = json_loads(request.body)
        tg_message_handler(data)
        return Response(status=status.HTTP_200_OK)


@extend_schema_view(
    create=extend_schema(
        summary="Метод не поддерживается",
        description="""
Для создания новой учетной записи используется адрес /users/register/
- Неавторизованный пользователь получит сообщение о необходимости авторизоваться.
- Авторизованному пользователю будет возвращена ошибка со статусом 405 - метод не поддерживается
""",
    ),
    list=extend_schema(
        summary="Отображение списка аккаунтов с пагинацией и фильтрацией",
        description="""
Необходима авторизация.
Авторизованному пользователю отображается список всех аккаунтов зарегистрированных пользователей.
""",
    ),
    retrieve=extend_schema(
        summary="Отображение деталей аккаунта",
        description="""
Необходима авторизация.
Авторизованному пользователю отображается вся имеющаяся информация об объекте без ограничений.
""",
    ),
    update=extend_schema(
        summary="Полное обновление аккаунта пользователя",
        description="""
Необходима авторизация и права владельца.
В теле запроса необходимо передать обязательные ключи "username", "email", "first_name" и "last_name"
с соответствующими значениями.
""",
    ),
    partial_update=extend_schema(
        summary="Частичное обновление аккаунта пользователя",
        description="""
Необходима авторизация и права владельца.
В теле запроса нужно указать новые значения для одного или нескольких полей "username", "email", "first_name",
"last_name".""",
    ),
    destroy=extend_schema(
        summary="Удаление аккаунта пользователя со всеми собственными привычками и расписаниями.",
        description="Необходима авторизация и права владельца.",
    ),
)
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
