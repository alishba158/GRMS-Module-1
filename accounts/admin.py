from django.contrib import admin
from .models import (
    Student, Supervisor, Synopsis, Thesis,
    ProgressReport, Meeting, ExtensionCase,
    DegreeLetter, Notification
)

# ============================================
# STUDENT ADMIN
# ============================================
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['registration_no', 'user', 'department', 'program', 'enrollment_status']
    list_filter = ['department', 'program', 'enrollment_status']
    search_fields = ['registration_no', 'user__first_name', 'user__last_name', 'user__email']

# ============================================
# SUPERVISOR ADMIN
# ============================================
@admin.register(Supervisor)
class SupervisorAdmin(admin.ModelAdmin):
    list_display = ['user', 'department', 'designation', 'availability_status']
    list_filter = ['department', 'availability_status']
    search_fields = ['user__first_name', 'user__last_name']

# ============================================
# SYNOPSIS ADMIN
# ============================================
@admin.register(Synopsis)
class SynopsisAdmin(admin.ModelAdmin):
    list_display = ['title', 'student', 'status', 'submission_date']
    list_filter = ['status']
    search_fields = ['title', 'student__registration_no']

# ============================================
# THESIS ADMIN
# ============================================
@admin.register(Thesis)
class ThesisAdmin(admin.ModelAdmin):
    list_display = ['title', 'student', 'status', 'submission_date']
    list_filter = ['status']
    search_fields = ['title', 'student__registration_no']

# ============================================
# PROGRESS REPORT ADMIN
# ============================================
@admin.register(ProgressReport)
class ProgressReportAdmin(admin.ModelAdmin):
    list_display = ['student', 'status', 'submission_date']
    list_filter = ['status']
    search_fields = ['student__registration_no']

# ============================================
# MEETING ADMIN (simplified)
# ============================================
@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ['student', 'supervisor', 'meeting_date']
    list_filter = ['meeting_date']
    search_fields = ['student__user__first_name']

# ============================================
# EXTENSION CASE ADMIN (simplified)
# ============================================
@admin.register(ExtensionCase)
class ExtensionCaseAdmin(admin.ModelAdmin):
    list_display = ['student', 'requested_duration', 'status', 'request_date']
    list_filter = ['status']
    search_fields = ['student__registration_no']

# ============================================
# DEGREE LETTER ADMIN (simplified)
# ============================================
@admin.register(DegreeLetter)
class DegreeLetterAdmin(admin.ModelAdmin):
    list_display = ['student', 'verification_status']
    list_filter = ['verification_status']
    search_fields = ['student__registration_no']

# ============================================
# NOTIFICATION ADMIN (simplified)
# ============================================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'message', 'is_read', 'created_at']
    list_filter = ['is_read']
    search_fields = ['user__username']