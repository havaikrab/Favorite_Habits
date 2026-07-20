import json
from datetime import datetime

from freezegun import freeze_time
from rest_framework import status
from rest_framework.test import APITestCase

from users.models import CustomUser

from .models import Habit, Schedule
from .services import prepare_events


class HabitTestCase(APITestCase):
    """Группа тестов связанных с обработкой объектов модели Habit"""

    fixtures = ["customuser_fixture.json", "habits_fixture.json", "schedule_fixture.json"]

    def setUp(self) -> None:
        """Наполнение БД тестовыми данными"""

        self.user = CustomUser.objects.get(email="user_5@mail.py")
        self.client.force_authenticate(user=self.user)

    def test_habit_creating(self) -> None:
        """Тест запроса на создание объекта модели Habit"""

        self.assertEqual(len(Habit.objects.all()), 10)
        url = "/habits/"
        response = self.client.post(
            url,
            data={
                "place": "new_place",
                "action": "new_action",
                "is_pleasant": True,
                "time_needed": 100,
                "is_public": False,
            },
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(Habit.objects.all()), 11)
        self.assertEqual(
            data,
            {
                "id": 11,
                "place": "new_place",
                "action": "new_action",
                "is_pleasant": True,
                "time_needed": 100,
                "is_public": False,
                "related_habit": None,
                "reward": None,
                "schedule": None,
            },
        )

    def test_habit_invalid_creating(self) -> None:
        """Тест запроса с невалидными данными на создание объекта модели Habit"""

        url = "/habits/"
        response = self.client.post(
            url,
            data={
                "place": "new_place",
                "action": "new_action",
                "is_pleasant": True,
                "time_needed": 100,
                "is_public": False,
                "reward": "new_reward",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_getting_own_habits_list(self) -> None:
        """Тест запроса на отображение списка объектов модели Habit их владельцу"""

        url = "/habits/?owner=True"
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data["results"]), 4)
        self.assertEqual(data["next"], None)

    def test_getting_public_habits_list(self) -> None:
        """Тест запроса на отображение списка объектов модели Habit с положительным признаком публичности"""

        url = "/habits/?public=True&page_size=10"
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data["results"]), 7)
        self.assertEqual(data["next"], None)

    def test_not_own_public_habit_retrieve(self) -> None:
        """Тест запроса на отображение объекта модели Habit с положительным признаком публичности
        пользователю, не являющемуся его владельцем"""

        habit = Habit.objects.get(action="action_4")
        url = f"/habits/{habit.pk}/"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "id": habit.pk,
                "place": "place_4",
                "action": "action_4",
                "is_pleasant": True,
                "related_habit": None,
                "reward": None,
                "time_needed": 40,
                "is_public": True,
                "schedule": "Каждые 2 часа",
            },
        )

    def test_habit_destroy(self) -> None:
        """Тест успешного запроса на удаление объекта модели Habit его владельцем"""

        self.assertEqual(len(Habit.objects.all()), 10)
        habit = Habit.objects.get(action="action_10")
        self.assertEqual(len(Schedule.objects.all()), 6)
        url = f"/habits/{habit.pk}/"
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(Habit.objects.all()), 9)
        self.assertEqual(len(Schedule.objects.all()), 5)


class ScheduleTestCase(APITestCase):
    """Группа тестов связанных с обработкой объектов модели Schedule"""

    fixtures = ["customuser_fixture.json", "habits_fixture.json", "schedule_fixture.json"]

    def setUp(self) -> None:
        """Наполнение БД тестовыми данными"""

        self.user = CustomUser.objects.get(email="user_4@mail.py")
        self.client.force_authenticate(user=self.user)

    def test_schedule_creating(self) -> None:
        """Тест запроса на создание объекта модели Schedule"""

        self.assertEqual(len(Schedule.objects.all()), 6)
        url = "/schedule/"
        response = self.client.post(
            url,
            data={
                "name": "Произвольное время",
                "habit": 6,
                "type": "times_in_month",
                "times_in_month": json.dumps([5000, 1000, 10000, 40000, 14900, 43000, 37888, 19999, 31500, 25111]),
                "start_at": "2026-07-19T00:00:00+07:00",
            },
        )
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(len(Schedule.objects.all()), 7)
        new_schedule = Schedule.objects.get(habit__pk=6)
        self.assertEqual(
            data,
            {
                "id": new_schedule.pk,
                "name": "Произвольное время",
                "habit": 6,
                "type": "times_in_month",
                "times_in_month": [5000, 1000, 10000, 40000, 14900, 43000, 37888, 19999, 31500, 25111],
                "constant_interval": None,
                "times_in_week": None,
                "start_at": "2026-07-19T00:00:00+07:00",
            },
        )
        self.assertEqual(new_schedule.next_event, 1784728800)
        time_zone = datetime.fromisoformat(new_schedule.start_at).tzinfo
        date_of_next_event = datetime.isoformat(datetime.fromtimestamp(new_schedule.next_event, tz=time_zone))
        self.assertEqual(date_of_next_event, "2026-07-22T21:00:00+07:00")

    def test_schedule_invalid_creating(self) -> None:
        """Тест запроса с невалидными данными на создание объекта модели Schedule"""

        url = "/schedule/"
        response = self.client.post(
            url,
            data={
                "name": "Произвольное время",
                "habit": 6,
                "type": "times_in_month",
                "times_in_month": [5500, 10000, 40000, 14900, 43000, 37888, 19999, 25111, 31500],
                "start_at": "2026-07-19T00:00:00+07:00",
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual("40060 <= required_value <= 40320" in str(response.json()), True)

    def test_getting_filtered_by_type_schedule_list(self) -> None:
        """Тест запроса на отображение списка объектов модели Schedule отсортированных по типу расписания"""

        url = "/schedule/?type=times_in_week"
        response = self.client.get(url)
        data = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data["results"]), 1)
        self.assertEqual(data["next"], None)
        self.assertEqual(
            data["results"][0],
            {
                "id": 5,
                "name": "По будням вечером",
                "habit": 5,
                "type": "times_in_week",
                "constant_interval": None,
                "times_in_week": [1320, 2760, 4200, 5640, 7080],
                "times_in_month": None,
                "start_at": "2026-07-19 09:06:44.242575+07:00",
            },
        )

    def test_schedule_update(self) -> None:
        """Тест успешного запроса на обновление объекта модели Schedule"""

        habit = Habit.objects.get(action="action_6")
        self.assertEqual(len(Schedule.objects.filter(habit=habit)), 0)
        schedule = Schedule.objects.get(name="Каждые 2 часа")
        url = f"/schedule/{schedule.pk}/"
        response = self.client.patch(
            url,
            data={
                "habit": habit.pk,
                "type": "times_in_week",
                "times_in_week": [120, 240, 360],
                "constant_interval": None,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        habit_url = f"/habits/{habit.pk}/"
        response = self.client.get(habit_url)
        self.assertEqual(
            response.json(),
            {
                "id": habit.pk,
                "place": "place_6",
                "action": "action_6",
                "is_pleasant": False,
                "related_habit": 2,
                "reward": None,
                "time_needed": 60,
                "is_public": True,
                "schedule": "Каждые 2 часа",
            },
        )


class ServiceFuncsTestCase(APITestCase):
    """Группа тестов для функций сервисного слоя"""

    fixtures = ["customuser_fixture.json", "habits_fixture.json", "schedule_fixture.json"]

    def setUp(self) -> None:
        """Наполнение БД тестовыми данными"""

        pass

    @freeze_time("2026-07-20T07:06:33+05:00")
    def test_updating_schedule_next_event(self) -> None:
        """Тест автоматического обновления поля next_event у объектов модели schedule"""

        prepare_events()
        freezed_time_obj = datetime.fromisoformat("2026-07-20T07:06:33+05:00")
        schedule_1 = Schedule.objects.get(habit__pk=10)
        next_event_date_1 = datetime.isoformat(
            datetime.fromtimestamp(schedule_1.next_event, tz=freezed_time_obj.tzinfo)
        )
        self.assertEqual(next_event_date_1, "2026-07-25T12:00:00+05:00")
        schedule_2 = Schedule.objects.get(habit__pk=4)
        next_event_date_2 = datetime.isoformat(
            datetime.fromtimestamp(schedule_2.next_event, tz=freezed_time_obj.tzinfo)
        )
        self.assertEqual(next_event_date_2, "2026-07-20T09:00:01+05:00")
