from rest_framework import status
from rest_framework.test import APITestCase

from .models import CustomUser


class CustomUserSpecialTestCase(APITestCase):
    """Тест процессов регистрации и авторизации пользователя"""

    def setUp(self) -> None:
        """Наполнение БД тестовыми данными"""

        pass

    def test_customuser_register(self) -> None:
        """Тест процессов регистрации и авторизации пользователя"""

        list_users_url = "/users/"
        unauthorized_response = self.client.get(list_users_url)
        self.assertEqual(unauthorized_response.status_code, status.HTTP_401_UNAUTHORIZED)

        register_url = "/users/register/"
        register_response = self.client.post(
            register_url,
            data={
                "username": "test_user",
                "email": "test@user.py",
                "first_name": "first_name",
                "last_name": "last_name",
                "password": "unusual_123",
                "password_confirm": "unusual_123",
            },
        )
        data = register_response.json()
        self.assertEqual(register_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            data,
            {
                "username": "test_user",
                "email": "test@user.py",
                "first_name": "first_name",
                "last_name": "last_name",
            },
        )

        login_url = "/users/login/"
        login_response = self.client.post(login_url, data={"email": "test@user.py", "password": "unusual_123"})
        authorized_user = CustomUser.objects.get(email="test@user.py")
        user_access_token = login_response.data.get("access")
        authorized_response = self.client.get(list_users_url, headers={"Authorization": f"Bearer {user_access_token}"})
        self.assertEqual(authorized_response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            authorized_response.data,
            [{"username": "test_user", "email": "test@user.py", "first_name": "first_name", "last_name": "last_name"}],
        )
        self.assertEqual(authorized_user.tg_chat_id, None)
        self.assertEqual(len(authorized_user.tg_secret), 16)


class CustomUserTestCase(APITestCase):
    """Группа тестов связанных с обработкой объектов модели CustomUser"""

    fixtures = ["customuser_fixture.json"]

    def setUp(self) -> None:
        """Наполнение БД тестовыми данными"""

        self.user = CustomUser.objects.get(email="user_5@mail.py")
        self.user.set_password("password")
        self.client.force_authenticate(user=self.user)

    def test_getting_users_list(self) -> None:
        """Тест запроса на получение списка всех зарегистрированных пользователей"""

        url = "/users/"
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            data,
            [
                {"username": "user_1", "email": "user_1@mail.py", "first_name": "Anton", "last_name": "Chekhov"},
                {"username": "user_2", "email": "user_2@mail.py", "first_name": "Fedor", "last_name": "Dostoevsky"},
                {"username": "user_3", "email": "user_3@mail.py", "first_name": "Mike", "last_name": "Lomonosov"},
                {"username": "user_4", "email": "user_4@mail.py", "first_name": "Alexandre", "last_name": "Dumas"},
                {"username": "user_5", "email": "user_5@mail.py", "first_name": "Petr", "last_name": "Petrov"},
            ],
        )

    def test_user_updating(self) -> None:
        """Тест запроса на изменение данных пользователя"""

        url = f"/users/{self.user.pk}/"
        response = self.client.patch(url, data={"first_name": "Arnold"})
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            data, {"username": "user_5", "email": "user_5@mail.py", "first_name": "Arnold", "last_name": "Petrov"}
        )
