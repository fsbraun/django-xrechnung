"""
URL configuration for tests.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("xrechnung/", include("django_xrechnung.urls")),
]
