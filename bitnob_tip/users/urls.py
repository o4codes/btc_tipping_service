from django.urls import path, include
from .views import UserCreateList, UserDetail

urlpatterns = [
    path("", UserCreateList.as_view(), name="user-create-list"),
    path("<str:sec_id>", UserDetail.as_view(), name="user-detail"),
]
