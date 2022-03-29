"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from swagger_render.views import SwaggerUIView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from api.core.views import webhook, status_check, redirect_docs

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/token", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/v1/token/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/", include("api.apps.users.urls")),
    path("api/v1/", include("api.apps.transactions.urls")),
    path("api/v1/webhook", webhook, name="webhook"),
    path("api/v1/health", status_check, name="status_check"),
    path('', SwaggerUIView.as_view()),
]

urlpatterns += static('/docs/', document_root='docs')