"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.http import JsonResponse

# A simple, clean message for your API homepage
def api_root_view(request):
    return JsonResponse({
        "status": "online",
        "project": "Dina Catering & Rentals API Backend",
        "message": "To access data, use the specific API endpoints or visit the admin portal.",
        "admin_portal": "/admin/"
    })

urlpatterns = [
    path('', api_root_view),
    path('admin/', admin.site.urls),
    path('api/', include('services.urls')),
]