from django.urls import path, include
from .views import UserCreateList, UserDetail

urlpatterns = [
    path("users", UserCreateList.as_view(), name="user-create-list"),
    path("users/<str:sec_id>", UserDetail.as_view(), name="user-detail"),
]
