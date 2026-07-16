from rest_framework.pagination import PageNumberPagination


class HabitsPaginator(PageNumberPagination):
    """Основной класс пагинации приложения habits"""

    page_size = 5
    page_size_query_param = "page_size"
    max_page_size = 10
