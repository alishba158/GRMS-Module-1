"""
URL configuration for grms_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
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
from django.urls import path
from django.contrib.auth import views as auth_views
from accounts import views

urlpatterns = [
    # Django admin panel
    path('admin/', admin.site.urls),

    # Login page
    path('', views.login_view, name='login'),

    # Dashboards (role based)
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/supervisor/', views.supervisor_dashboard, name='supervisor_dashboard'),
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),

    # Logout
    path('logout/', views.logout_view, name='logout'),
]


