from django.urls import path
from .views import (
    login_view,
    admin_dashboard,
    supervisor_dashboard,
    student_dashboard
)

urlpatterns = [
    path('', login_view, name='login'),

    # dashboards (IMPORTANT: admin/ mat likhna)
    path('dashboard/admin/', admin_dashboard, name='admin_dashboard'),
    path('dashboard/supervisor/', supervisor_dashboard, name='supervisor_dashboard'),
    path('dashboard/student/', student_dashboard, name='student_dashboard'),
]
