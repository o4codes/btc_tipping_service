from django.urls import path, include
from .views import UserCreateList

urlpatterns = [
    path('', UserCreateList.as_view(), name='user-create-list'),
]