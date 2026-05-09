from django.urls import path
from . import views

urlpatterns = [
    # ===== HOME =====
    path('', views.home_view, name='home'),

    # ===== AUTH =====
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),

    # ===== ADMIN DASHBOARD & ACTIONS =====
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('assign-supervisor/<int:synopsis_id>/', views.assign_supervisor, name='assign_supervisor'),
    path('approve-synopsis/<int:synopsis_id>/', views.approve_synopsis, name='approve_synopsis'),
    path('reject-synopsis/<int:synopsis_id>/', views.reject_synopsis, name='reject_synopsis'),

    # ===== ADMIN STUDENT MANAGEMENT =====
    path('admin/students/', views.admin_student_list, name='admin_student_list'),
    path('admin/students/create/', views.admin_student_create, name='admin_student_create'),
    path('admin/students/<int:pk>/', views.admin_student_detail, name='admin_student_detail'),
    path('admin/students/<int:pk>/update/', views.admin_student_update, name='admin_student_update'),
    path('admin/students/<int:pk>/delete/', views.admin_student_delete, name='admin_student_delete'),

    # ===== ADMIN SUPERVISOR MANAGEMENT =====
    path('admin/supervisors/', views.admin_supervisor_list, name='admin_supervisor_list'),
    path('admin/supervisors/create/', views.admin_supervisor_create, name='admin_supervisor_create'),
    path('admin/supervisors/<int:pk>/', views.admin_supervisor_detail, name='admin_supervisor_detail'),
    path('admin/supervisors/<int:pk>/update/', views.admin_supervisor_update, name='admin_supervisor_update'),
    path('admin/supervisors/<int:pk>/delete/', views.admin_supervisor_delete, name='admin_supervisor_delete'),

    # ===== ADMIN SYNOPSIS MANAGEMENT =====
    path('admin/synopsis/', views.admin_synopsis_list, name='admin_synopsis_list'),
    path('admin/synopsis/<int:pk>/', views.admin_synopsis_detail, name='admin_synopsis_detail'),
    path('admin/synopsis/<int:pk>/assign/', views.admin_synopsis_assign, name='admin_synopsis_assign'),
    path('admin/synopsis/<int:pk>/approve/', views.admin_synopsis_approve, name='admin_synopsis_approve'),
    path('admin/synopsis/<int:pk>/reject/', views.admin_synopsis_reject, name='admin_synopsis_reject'),

    # ===== ADMIN THESIS MANAGEMENT =====
    path('admin/thesis/', views.admin_thesis_list, name='admin_thesis_list'),
    path('admin/thesis/<int:pk>/', views.admin_thesis_detail, name='admin_thesis_detail'),
    path('admin/thesis/<int:pk>/update-status/', views.admin_thesis_update_status, name='admin_thesis_update_status'),
    # Thesis examiner assignment, viva, finalize
    path('admin/thesis/<int:pk>/assign-examiners/', views.admin_thesis_assign_examiners, name='admin_thesis_assign_examiners'),
    path('admin/thesis/<int:pk>/record-viva/', views.admin_thesis_record_viva, name='admin_thesis_record_viva'),
    path('admin/thesis/<int:pk>/finalize/', views.admin_thesis_finalize, name='admin_thesis_finalize'),

    # ===== ADMIN PROGRESS REPORTS MANAGEMENT =====
    path('admin/progress/', views.admin_progress_list, name='admin_progress_list'),
    path('admin/progress/<int:pk>/', views.admin_progress_detail, name='admin_progress_detail'),

    # ===== ADMIN MEETINGS MANAGEMENT =====
    path('admin/meetings/', views.admin_meeting_list, name='admin_meeting_list'),
    path('admin/meetings/<int:pk>/', views.admin_meeting_detail, name='admin_meeting_detail'),

    # ===== ADMIN EXTENSIONS MANAGEMENT =====
    path('admin/extensions/', views.admin_extension_list, name='admin_extension_list'),
    path('admin/extensions/<int:pk>/', views.admin_extension_detail, name='admin_extension_detail'),
    path('admin/extensions/<int:pk>/approve/', views.admin_extension_approve, name='admin_extension_approve'),
    path('admin/extensions/<int:pk>/reject/', views.admin_extension_reject, name='admin_extension_reject'),

    # ===== ADMIN DEGREE LETTER MANAGEMENT (NEW) =====
    path('admin/degree/', views.admin_degree_list, name='admin_degree_list'),
    path('admin/degree/<int:pk>/', views.admin_degree_detail, name='admin_degree_detail'),
    path('admin/degree/<int:pk>/verify/', views.admin_degree_verify, name='admin_degree_verify'),
    path('admin/degree/<int:pk>/issue/', views.admin_degree_issue, name='admin_degree_issue'),

    # ===== SUPERVISOR DASHBOARD =====
    path('supervisor-dashboard/', views.supervisor_dashboard, name='supervisor_dashboard'),

    # ===== SUPERVISOR SYNOPSIS =====
    path('supervisor/synopsis/', views.supervisor_synopsis_list, name='supervisor_synopsis_list'),
    path('supervisor/synopsis/<int:pk>/review/', views.supervisor_synopsis_review, name='supervisor_synopsis_review'),
    path('supervisor/synopsis/<int:pk>/', views.supervisor_synopsis_detail, name='supervisor_synopsis_detail'),
    path('supervisor/synopsis/<int:pk>/approve/', views.supervisor_synopsis_approve, name='supervisor_synopsis_approve'),
    path('supervisor/synopsis/<int:pk>/reject/', views.supervisor_synopsis_reject, name='supervisor_synopsis_reject'),

    # ===== SUPERVISOR THESIS =====
    path('supervisor/thesis/', views.supervisor_thesis_list, name='supervisor_thesis_list'),
    path('supervisor/thesis/<int:pk>/', views.supervisor_thesis_detail, name='supervisor_thesis_detail'),
    path('supervisor/thesis/<int:pk>/update-status/', views.supervisor_thesis_update_status, name='supervisor_thesis_update_status'),

    # ===== SUPERVISOR MEETINGS =====
    path('supervisor/meetings/', views.supervisor_meeting_list, name='supervisor_meeting_list'),
    path('supervisor/meetings/create/', views.supervisor_meeting_create, name='supervisor_meeting_create'),
    path('supervisor/meetings/<int:pk>/', views.supervisor_meeting_detail, name='supervisor_meeting_detail'),
    path('supervisor/meetings/<int:pk>/update/', views.supervisor_meeting_update, name='supervisor_meeting_update'),

    # ===== SUPERVISOR EXTENSIONS =====
    path('supervisor/extensions/', views.supervisor_extension_list, name='supervisor_extension_list'),
    path('supervisor/extensions/<int:pk>/', views.supervisor_extension_detail, name='supervisor_extension_detail'),
    path('supervisor/extensions/<int:pk>/review/', views.supervisor_extension_review, name='supervisor_extension_review'),

    # ===== SUPERVISOR PROGRESS =====
    path('supervisor/progress/', views.supervisor_progress_list, name='supervisor_progress_list'),
    path('supervisor/progress/<int:pk>/review/', views.supervisor_progress_review, name='supervisor_progress_review'),
    path('supervisor/progress/<int:pk>/', views.supervisor_progress_detail, name='supervisor_progress_detail'),

    # ===== SUPERVISOR PROFILE =====
    path('supervisor/profile/update/', views.supervisor_profile_update, name='supervisor_profile_update'),
    path('supervisor/profile/change-password/', views.supervisor_change_password, name='supervisor_change_password'),

    # ===== EXAMINER =====
    path('examiner/dashboard/', views.examiner_dashboard, name='examiner_dashboard'),
    path('examiner/thesis/<int:pk>/', views.examiner_thesis_detail, name='examiner_thesis_detail'),
    path('examiner/evaluation/<int:pk>/submit/', views.examiner_evaluation_submit, name='examiner_evaluation_submit'),

    # ===== NOTIFICATIONS (COMMON) =====
    path('notifications/mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('notifications/', views.all_notifications, name='all_notifications'),

    # ===== STUDENT DASHBOARD =====
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    
    # ===== STUDENT SYNOPSIS =====
    path('student/synopsis/', views.student_synopsis_list, name='student_synopsis_list'),
    path('student/synopsis/create/', views.student_synopsis_create, name='student_synopsis_create'),
    path('student/synopsis/submit/', views.student_synopsis_submit, name='student_synopsis_submit'),
    path('student/synopsis/<int:pk>/resubmit/', views.student_synopsis_resubmit, name='student_synopsis_resubmit'),
    path('student/synopsis/<int:pk>/', views.student_synopsis_detail, name='student_synopsis_detail'),
    
    # ===== STUDENT THESIS =====
    path('student/thesis/', views.student_thesis_list, name='student_thesis_list'),
    path('student/thesis/create/', views.student_thesis_create, name='student_thesis_create'),
    path('student/thesis/<int:pk>/', views.student_thesis_detail, name='student_thesis_detail'),
    
    # ===== STUDENT PROGRESS REPORTS =====
    path('student/progress/', views.student_progress_list, name='student_progress_list'),
    path('student/progress/create/', views.student_progress_create, name='student_progress_create'),
    path('student/progress/<int:pk>/', views.student_progress_detail, name='student_progress_detail'),
    
    # ===== STUDENT MEETINGS =====
    path('student/meetings/', views.student_meeting_list, name='student_meeting_list'),
    path('student/meetings/<int:pk>/', views.student_meeting_detail, name='student_meeting_detail'),
    
    # ===== STUDENT EXTENSIONS =====
    path('student/extensions/', views.student_extension_list, name='student_extension_list'),
    path('student/extensions/create/', views.student_extension_create, name='student_extension_create'),
    path('student/extensions/<int:pk>/', views.student_extension_detail, name='student_extension_detail'),
    
    # ===== STUDENT DEGREE LETTER =====
    path('student/degree/request/', views.student_degree_request, name='student_degree_request'),
    
    # ===== STUDENT PROFILE =====
    path('student/profile/update/', views.student_profile_update, name='student_profile_update'),
    path('student/profile/change-password/', views.student_change_password, name='student_change_password'),

    # ===== REPORTS & ANALYTICS =====
    path('reports/', views.reports_dashboard, name='reports_dashboard'),
    path('reports/student-progress/', views.student_progress_report, name='student_progress_report'),
    path('reports/supervisor-workload/', views.supervisor_workload_report, name='supervisor_workload_report'),
    path('reports/chart-data/', views.submission_stats_chart, name='submission_stats_chart'),
]