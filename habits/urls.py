from rest_framework.routers import DefaultRouter

from . import views
from .apps import HabitsConfig

app_name = HabitsConfig.name

habits_router = DefaultRouter()
habits_router.register("habits", views.HabitViewSet)

urlpatterns: list = []
urlpatterns += habits_router.urls
