import csv
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User, Group
from django.contrib import messages
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models import Q, Count
from django.http import HttpResponse, JsonResponse, Http404
from django.urls import reverse  # for notification links
import pandas as pd
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import openpyxl

# Import forms (including extension forms and degree letter form)
from .forms import (
    SynopsisSubmitForm, SynopsisReviewForm,
    ProgressReportSubmitForm, ProgressReportReviewForm,
    ThesisAssignmentForm, ExaminerReportForm, VivaResultForm,
    ExtensionRequestForm, ExtensionReviewForm,
    DegreeLetterVerificationForm   # ← ADDED
)

print("✅ views.py loaded successfully")

from .models import (
    Student, Supervisor, Synopsis, Thesis, ProgressReport,
    Meeting, ExtensionCase, DegreeLetter, Notification, Examiner,
    ThesisEvaluation
)


# ======================
# ADMIN CHECK (defined early for decorators)
# ======================
def is_admin(user):
    return user.is_superuser or user.groups.filter(name='Admin').exists()


# =================================================
# REPORTS & ANALYTICS
# =================================================
@login_required
@user_passes_test(is_admin)
def reports_dashboard(request):
    """Main reports dashboard with filters"""
    departments = Student.objects.values_list('department', flat=True).distinct()
    programs = Student.objects.values_list('program', flat=True).distinct()
    
    # Default date range (last 30 days)
    end_date = timezone.now().date()
    start_date = end_date - datetime.timedelta(days=30)
    
    context = {
        'departments': departments,
        'programs': programs,
        'start_date': start_date.strftime('%Y-%m-%d'),
        'end_date': end_date.strftime('%Y-%m-%d'),
    }
    return render(request, 'reports/dashboard.html', context)


@login_required
@user_passes_test(is_admin)
def student_progress_report(request):
    """Generate student progress report"""
    # Get filter parameters
    dept = request.GET.get('department', '')
    program = request.GET.get('program', '')
    start_date = request.GET.get('start_date', '')
    end_date = request.GET.get('end_date', '')
    format_type = request.GET.get('format', 'html')  # html, pdf, excel, csv
    
    # Base queryset
    students = Student.objects.select_related('user').all()
    
    # Apply filters
    if dept:
        students = students.filter(department=dept)
    if program:
        students = students.filter(program=program)
    
    # Prepare data
    data = []
    for student in students:
        synopses = Synopsis.objects.filter(student=student)
        theses = Thesis.objects.filter(student=student)
        reports = ProgressReport.objects.filter(student=student)
        meetings = Meeting.objects.filter(student=student)
        extensions = ExtensionCase.objects.filter(student=student)
        
        data.append({
            'reg_no': student.registration_no,
            'name': student.user.get_full_name(),
            'department': student.department,
            'program': student.program,
            'session': student.session,
            'enrollment_status': student.enrollment_status,
            'synopsis_count': synopses.count(),
            'synopsis_approved': synopses.filter(status='Approved').count(),
            'synopsis_pending': synopses.filter(status='Pending').count(),
            'thesis_count': theses.count(),
            'thesis_approved': theses.filter(status='Approved').count(),
            'thesis_pending': theses.filter(status='Submitted').count(),
            'reports_count': reports.count(),
            'meetings_count': meetings.count(),
            'extensions_count': extensions.count(),
            'extensions_approved': extensions.filter(status='Approved').count(),
        })
    
    # Handle different formats
    if format_type == 'csv':
        return export_csv(data)
    elif format_type == 'excel':
        return export_excel(data)
    elif format_type == 'pdf':
        return export_pdf(data)
    else:
        return JsonResponse(data, safe=False)


def export_csv(data):
    """Export as CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="student_report_{timezone.now().date()}.csv"'
    
    writer = csv.DictWriter(response, fieldnames=data[0].keys() if data else [])
    writer.writeheader()
    writer.writerows(data)
    return response


def export_excel(data):
    """Export as Excel"""
    df = pd.DataFrame(data)
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="student_report_{timezone.now().date()}.xlsx"'
    df.to_excel(response, index=False, engine='openpyxl')
    return response


def export_pdf(data):
    """Export as PDF"""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="student_report_{timezone.now().date()}.pdf"'
    
    # Create PDF
    doc = SimpleDocTemplate(response, pagesize=A4)
    elements = []
    
    # Title
    styles = getSampleStyleSheet()
    elements.append(Paragraph("Student Progress Report", styles['Title']))
    elements.append(Paragraph(f"Generated on: {timezone.now().date()}", styles['Normal']))
    
    # Table data
    if data:
        table_data = [list(data[0].keys())]  # Header
        for row in data:
            table_data.append(list(row.values()))
        
        table = Table(table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.green),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        elements.append(table)
    
    doc.build(elements)
    return response


@login_required
@user_passes_test(is_admin)
def supervisor_workload_report(request):
    """Generate supervisor workload report"""
    supervisors = Supervisor.objects.select_related('user').prefetch_related('students').all()
    
    data = []
    for sup in supervisors:
        students = sup.students.all()
        synopses = Synopsis.objects.filter(supervisor=sup)
        theses = Thesis.objects.filter(student__in=students)
        
        data.append({
            'name': sup.user.get_full_name(),
            'department': sup.department,
            'designation': sup.designation,
            'students_count': students.count(),
            'synopses_count': synopses.count(),
            'synopses_pending': synopses.filter(status='Pending').count(),
            'synopses_approved': synopses.filter(status='Approved').count(),
            'theses_count': theses.count(),
            'theses_under_review': theses.filter(status='Under Review').count(),
            'theses_approved': theses.filter(status='Approved').count(),
            'availability': sup.availability_status,
        })
    
    format_type = request.GET.get('format', 'html')
    if format_type == 'csv':
        return export_csv(data)
    elif format_type == 'excel':
        return export_excel(data)
    else:
        return JsonResponse(data, safe=False)


@login_required
@user_passes_test(is_admin)
def submission_stats_chart(request):
    """Return JSON data for charts"""
    # Last 6 months
    months = []
    synopsis_counts = []
    thesis_counts = []
    
    for i in range(5, -1, -1):
        month = timezone.now() - datetime.timedelta(days=30*i)
        month_name = month.strftime('%b %Y')
        months.append(month_name)
        
        start = month.replace(day=1, hour=0, minute=0, second=0)
        end = (start + datetime.timedelta(days=32)).replace(day=1) - datetime.timedelta(seconds=1)
        
        synopsis_counts.append(Synopsis.objects.filter(submission_date__range=[start, end]).count())
        thesis_counts.append(Thesis.objects.filter(submission_date__range=[start, end]).count())
    
    return JsonResponse({
        'months': months,
        'synopsis': synopsis_counts,
        'thesis': thesis_counts,
    })


# ======================
# HOME
# ======================
def home_view(request):
    return render(request, 'home.html')


# ======================
# LOGIN (UPDATED with Examiner)
# ======================
def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)

            if user.is_superuser or user.groups.filter(name='Admin').exists():
                return redirect('admin_dashboard')
            elif user.groups.filter(name='Supervisor').exists():
                return redirect('supervisor_dashboard')
            elif user.groups.filter(name='Examiner').exists():
                return redirect('examiner_dashboard')
            else:
                return redirect('student_dashboard')

        messages.error(request, "Invalid username or password")

    return render(request, 'auth/login.html')


# ======================
# REGISTER
# ======================
def register_view(request):
    if request.method == "POST":
        fullname = request.POST.get("fullname")
        username = request.POST.get("username")
        email = request.POST.get("email")
        role = request.POST.get("role")
        password = request.POST.get("password")
        confirm = request.POST.get("confirm_password")

        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect("register")

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=fullname
        )

        group, _ = Group.objects.get_or_create(name=role)
        user.groups.add(group)

        if role == 'Student':
            Student.objects.create(
                user=user,
                registration_no=f"TEMP-{user.id}",
                department='Not Assigned',
                session='Not Assigned',
                program='Not Assigned',
                enrollment_status='Active',
                admission_date=timezone.now().date()
            )
        elif role == 'Supervisor':
            Supervisor.objects.create(
                user=user,
                department='Not Assigned',
                designation='Not Assigned',
                availability_status='Available'
            )

        messages.success(request, "Account created successfully. Please login.")
        return redirect("login")

    return render(request, 'auth/register.html')


# ======================
# LOGOUT
# ======================
@login_required
def logout_view(request):
    logout(request)
    return redirect("login")


# =================================================
# ADMIN DASHBOARD
# =================================================
@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    total_students = Student.objects.count()
    active_students = Student.objects.filter(user__is_active=True).count()
    total_supervisors = Supervisor.objects.count()
    available_supervisors = Supervisor.objects.filter(availability_status='Available').count()
    pending_synopses = Synopsis.objects.filter(status='Pending').count()
    pending_theses = Thesis.objects.filter(status='Under Review').count()
    pending_extensions = ExtensionCase.objects.filter(status='Pending').count()
    
    # Urgent extensions (pending > 7 days)
    urgent_extensions = ExtensionCase.objects.filter(
        status='Pending',
        request_date__lte=timezone.now() - datetime.timedelta(days=7)
    ).count()
    
    recent_students = Student.objects.select_related('user').order_by('-admission_date')[:5]
    recent_synopses = Synopsis.objects.select_related('student').order_by('-submission_date')[:5]
    recent_theses = Thesis.objects.select_related('student').order_by('-submission_date')[:5]
    recent_extensions = ExtensionCase.objects.select_related('student').order_by('-request_date')[:5]
    
    # Notifications for admin
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    
    context = {
        'total_students': total_students,
        'active_students': active_students,
        'total_supervisors': total_supervisors,
        'available_supervisors': available_supervisors,
        'pending_synopses': pending_synopses,
        'pending_theses': pending_theses,
        'pending_extensions': pending_extensions,
        'urgent_extensions': urgent_extensions,
        'recent_students': recent_students,
        'recent_synopses': recent_synopses,
        'recent_theses': recent_theses,
        'recent_extensions': recent_extensions,
        'unread_notifications': unread_notifications,
        'unread_count': unread_count,
    }
    return render(request, 'admin/dashboard.html', context)


# =================================================
# ASSIGN SUPERVISOR TO SYNOPSIS
# =================================================
@login_required
@user_passes_test(is_admin)
def assign_supervisor(request, synopsis_id):
    synopsis = get_object_or_404(Synopsis, id=synopsis_id)
    if request.method == "POST":
        supervisor_id = request.POST.get("supervisor")
        supervisor = get_object_or_404(Supervisor, id=supervisor_id)
        synopsis.supervisor = supervisor
        synopsis.status = "Assigned"
        synopsis.save()
        messages.success(request, "Supervisor assigned successfully")
    return redirect("admin_dashboard")


# =================================================
# APPROVE / REJECT SYNOPSIS (ADMIN)
# =================================================
@login_required
@user_passes_test(is_admin)
def approve_synopsis(request, synopsis_id):
    synopsis = get_object_or_404(Synopsis, id=synopsis_id)
    synopsis.status = "Approved"
    synopsis.save()
    messages.success(request, "Synopsis approved")
    return redirect("admin_dashboard")


@login_required
@user_passes_test(is_admin)
def reject_synopsis(request, synopsis_id):
    synopsis = get_object_or_404(Synopsis, id=synopsis_id)
    synopsis.status = "Rejected"
    synopsis.save()
    messages.error(request, "Synopsis rejected")
    return redirect("admin_dashboard")


# =================================================
# SUPERVISOR DASHBOARD (ENHANCED)
# =================================================
@login_required
def supervisor_dashboard(request):
    try:
        supervisor = Supervisor.objects.get(user=request.user)
    except Supervisor.DoesNotExist:
        messages.error(request, "Supervisor profile not found.")
        return redirect("home")
    
    # Assigned students
    assigned_students = Student.objects.filter(supervisor=supervisor)
    student_ids = assigned_students.values_list('id', flat=True)
    
    # Stats
    total_students = assigned_students.count()
    pending_synopses = Synopsis.objects.filter(supervisor=supervisor, status='Pending').count()
    pending_theses = Thesis.objects.filter(student__supervisor=supervisor, status='Under Review').count()
    pending_reports = ProgressReport.objects.filter(student_id__in=student_ids, status='Submitted').count()
    pending_extensions = ExtensionCase.objects.filter(student_id__in=student_ids, status='Pending').count()
    
    # Upcoming meetings
    upcoming_meetings = Meeting.objects.filter(
        supervisor=supervisor,
        meeting_date__gte=timezone.now()
    ).order_by('meeting_date')[:5]
    
    # Recent items
    recent_synopses = Synopsis.objects.filter(supervisor=supervisor).order_by('-submission_date')[:5]
    recent_theses = Thesis.objects.filter(student__supervisor=supervisor).order_by('-submission_date')[:5]
    recent_meetings = Meeting.objects.filter(supervisor=supervisor).order_by('-meeting_date')[:5]
    recent_extensions = ExtensionCase.objects.filter(student_id__in=student_ids).order_by('-request_date')[:5]
    
    # Notifications
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    
    context = {
        'supervisor': supervisor,
        'total_students': total_students,
        'pending_synopses': pending_synopses,
        'pending_theses': pending_theses,
        'pending_reports': pending_reports,
        'pending_extensions': pending_extensions,
        'upcoming_meetings': upcoming_meetings,
        'recent_synopses': recent_synopses,
        'recent_theses': recent_theses,
        'recent_meetings': recent_meetings,
        'recent_extensions': recent_extensions,
        'unread_notifications': unread_notifications,
        'unread_count': unread_count,
    }
    return render(request, 'supervisor/dashboard.html', context)


# =================================================
# SUPERVISOR SYNOPSIS REVIEW
# =================================================
@login_required
def supervisor_synopsis_list(request):
    supervisor = get_object_or_404(Supervisor, user=request.user)
    synopses = Synopsis.objects.filter(
        Q(supervisor=supervisor) | Q(student__supervisor=supervisor)
    ).distinct().order_by('-submission_date')
    
    search_query = request.GET.get('search', '')
    if search_query:
        synopses = synopses.filter(
            Q(title__icontains=search_query) |
            Q(student__user__first_name__icontains=search_query) |
            Q(student__user__last_name__icontains=search_query)
        )
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        synopses = synopses.filter(status=status_filter)
    
    context = {
        'synopses': synopses,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': Synopsis.STATUS_CHOICES,
    }
    return render(request, 'supervisor/synopsis/list.html', context)


@login_required
def supervisor_synopsis_detail(request, pk):
    try:
        supervisor = Supervisor.objects.get(user=request.user)
    except Supervisor.DoesNotExist:
        messages.error(request, "Supervisor profile not found.")
        return redirect('home')
    
    synopsis = get_object_or_404(Synopsis, pk=pk)
    
    if not (synopsis.supervisor == supervisor or synopsis.student.supervisor == supervisor):
        raise Http404("No Synopsis matches the given query.")
    
    return render(request, 'supervisor/synopsis/detail.html', {'synopsis': synopsis})


@login_required
def supervisor_synopsis_approve(request, pk):
    supervisor = get_object_or_404(Supervisor, user=request.user)
    synopsis = get_object_or_404(Synopsis, pk=pk)
    
    if not (synopsis.supervisor == supervisor or synopsis.student.supervisor == supervisor):
        messages.error(request, "You are not authorized to approve this synopsis.")
        return redirect('supervisor_synopsis_list')
    
    if request.method == 'POST':
        remarks = request.POST.get('remarks', '')
        synopsis.status = 'Approved'
        synopsis.remarks = remarks
        synopsis.save()
        Notification.objects.create(
            user=synopsis.student.user,
            notification_type='System',
            message=f'Your synopsis "{synopsis.title}" has been approved.',
            link=f'/student/synopsis/{synopsis.id}/'
        )
        messages.success(request, 'Synopsis approved successfully!')
    return redirect('supervisor_synopsis_list')


@login_required
def supervisor_synopsis_reject(request, pk):
    supervisor = get_object_or_404(Supervisor, user=request.user)
    synopsis = get_object_or_404(Synopsis, pk=pk)
    
    if not (synopsis.supervisor == supervisor or synopsis.student.supervisor == supervisor):
        messages.error(request, "You are not authorized to reject this synopsis.")
        return redirect('supervisor_synopsis_list')
    
    if request.method == 'POST':
        remarks = request.POST.get('remarks', '')
        synopsis.status = 'Rejected'
        synopsis.remarks = remarks
        synopsis.save()
        Notification.objects.create(
            user=synopsis.student.user,
            notification_type='System',
            message=f'Your synopsis "{synopsis.title}" has been rejected.',
            link=f'/student/synopsis/{synopsis.id}/'
        )
        messages.success(request, 'Synopsis rejected.')
    return redirect('supervisor_synopsis_list')


@login_required
def supervisor_synopsis_review(request, pk):
    synopsis = get_object_or_404(Synopsis, pk=pk)
    supervisor = get_object_or_404(Supervisor, user=request.user)
    
    if not (synopsis.supervisor == supervisor or synopsis.student.supervisor == supervisor):
        messages.error(request, "You are not authorized to review this synopsis.")
        return redirect('supervisor_dashboard')
    
    if request.method == 'POST':
        form = SynopsisReviewForm(request.POST, instance=synopsis)
        if form.is_valid():
            synopsis = form.save(commit=False)
            synopsis.reviewed_by = supervisor
            synopsis.review_date = timezone.now()
            synopsis.save()
            
            Notification.objects.create(
                user=synopsis.student.user,
                notification_type='System',
                message=f"Your synopsis '{synopsis.title}' has been {synopsis.get_status_display()}.",
                link=f"/student/synopsis/{synopsis.id}/"
            )
            messages.success(request, "Review submitted.")
            return redirect('supervisor_synopsis_list')
    else:
        form = SynopsisReviewForm(instance=synopsis)
    return render(request, 'supervisor/synopsis/review.html', {'form': form, 'synopsis': synopsis})


# =================================================
# SUPERVISOR THESIS REVIEW
# =================================================
@login_required
def supervisor_thesis_list(request):
    supervisor = get_object_or_404(Supervisor, user=request.user)
    theses = Thesis.objects.filter(student__supervisor=supervisor).order_by('-submission_date')
    return render(request, 'supervisor/thesis/list.html', {'theses': theses})


@login_required
def supervisor_thesis_detail(request, pk):
    thesis = get_object_or_404(Thesis, pk=pk, student__supervisor__user=request.user)
    return render(request, 'supervisor/thesis/detail.html', {'thesis': thesis})


@login_required
def supervisor_thesis_update_status(request, pk):
    thesis = get_object_or_404(Thesis, pk=pk, student__supervisor__user=request.user)
    if request.method == 'POST':
        status = request.POST.get('status')
        remarks = request.POST.get('remarks', '')
        if status:
            thesis.status = status
            thesis.remarks = remarks
            thesis.save()
            Notification.objects.create(
                user=thesis.student.user,
                notification_type='System',
                message=f'Your thesis status has been updated to {status}.',
                link=f'/student/thesis/{thesis.id}/'
            )
            messages.success(request, f'Thesis status updated to {status}.')
    return redirect('supervisor_thesis_list')


# =================================================
# SUPERVISOR MEETINGS
# =================================================
@login_required
def supervisor_meeting_list(request):
    supervisor = get_object_or_404(Supervisor, user=request.user)
    meetings = Meeting.objects.filter(supervisor=supervisor).order_by('-meeting_date')
    return render(request, 'supervisor/meeting/list.html', {'meetings': meetings})


@login_required
def supervisor_meeting_create(request):
    supervisor = get_object_or_404(Supervisor, user=request.user)
    students = Student.objects.filter(supervisor=supervisor)
    if request.method == 'POST':
        student_id = request.POST.get('student')
        date = request.POST.get('date')
        time = request.POST.get('time')
        mode = request.POST.get('mode')
        agenda = request.POST.get('agenda')
        if student_id and date and time and mode:
            meeting_date = timezone.datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
            meeting = Meeting.objects.create(
                student_id=student_id,
                supervisor=supervisor,
                meeting_date=meeting_date,
                mode=mode,
                agenda=agenda
            )
            Notification.objects.create(
                user=meeting.student.user,
                notification_type='System',
                message=f'New meeting scheduled on {meeting_date.strftime("%b %d, %Y at %I:%M %p")}',
                link=f'/student/meetings/{meeting.id}/'
            )
            messages.success(request, 'Meeting scheduled successfully!')
            return redirect('supervisor_meeting_list')
        else:
            messages.error(request, 'Please fill all required fields.')
    context = {'students': students}
    return render(request, 'supervisor/meeting/create.html', context)


@login_required
def supervisor_meeting_detail(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk, supervisor__user=request.user)
    return render(request, 'supervisor/meeting/detail.html', {'meeting': meeting})


@login_required
def supervisor_meeting_update(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk, supervisor__user=request.user)
    if request.method == 'POST':
        summary = request.POST.get('summary')
        minutes = request.FILES.get('minutes')
        if summary:
            meeting.summary = summary
            if minutes:
                meeting.minutes_file = minutes
            meeting.save()
            messages.success(request, 'Meeting updated successfully!')
            return redirect('supervisor_meeting_detail', pk=meeting.id)
    return render(request, 'supervisor/meeting/update.html', {'meeting': meeting})


# =================================================
# SUPERVISOR EXTENSION REQUESTS (UPDATED)
# =================================================

@login_required
def supervisor_extension_list(request):
    supervisor = get_object_or_404(Supervisor, user=request.user)
    extensions = ExtensionCase.objects.filter(student__supervisor=supervisor).order_by('-request_date')
    return render(request, 'supervisor/extension/list.html', {'extensions': extensions})


@login_required
def supervisor_extension_detail(request, pk):
    extension = get_object_or_404(ExtensionCase, pk=pk, student__supervisor__user=request.user)
    return render(request, 'supervisor/extension/detail.html', {'extension': extension})


@login_required
def supervisor_extension_review(request, pk):
    extension = get_object_or_404(ExtensionCase, pk=pk, student__supervisor__user=request.user)
    if request.method == 'POST':
        form = ExtensionReviewForm(request.POST, instance=extension)
        if form.is_valid():
            ext = form.save(commit=False)
            if ext.status in ['Approved', 'Rejected']:
                ext.approval_date = timezone.now().date()
            ext.save()
            # Notify student
            Notification.objects.create(
                user=extension.student.user,
                notification_type='System',
                message=f"Your extension request has been {ext.status}.",
                link=reverse('student_extension_detail', args=[extension.id])
            )
            messages.success(request, f"Extension {ext.status}.")
            return redirect('supervisor_extension_list')
    else:
        form = ExtensionReviewForm(instance=extension)
    return render(request, 'supervisor/extension/review.html', {'form': form, 'extension': extension})


# =================================================
# SUPERVISOR PROFILE
# =================================================
@login_required
def supervisor_profile_update(request):
    supervisor = get_object_or_404(Supervisor, user=request.user)
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        supervisor.department = request.POST.get('department', supervisor.department)
        supervisor.designation = request.POST.get('designation', supervisor.designation)
        supervisor.availability_status = request.POST.get('availability', supervisor.availability_status)
        supervisor.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('supervisor_dashboard')
    return render(request, 'supervisor/profile/update.html', {'supervisor': supervisor})


@login_required
def supervisor_change_password(request):
    if request.method == 'POST':
        old = request.POST.get('old_password')
        new1 = request.POST.get('new_password1')
        new2 = request.POST.get('new_password2')
        if not request.user.check_password(old):
            messages.error(request, 'Old password is incorrect.')
        elif new1 != new2:
            messages.error(request, 'New passwords do not match.')
        elif len(new1) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
        else:
            request.user.set_password(new1)
            request.user.save()
            messages.success(request, 'Password changed successfully! Please login again.')
            return redirect('login')
    return render(request, 'supervisor/profile/change_password.html')


# =================================================
# STUDENT DASHBOARD (ENHANCED)
# =================================================
@login_required
def student_dashboard(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found. Please contact admin.")
        return redirect('home')
    
    # Stats
    synopsis_status = Synopsis.objects.filter(student=student).first()
    thesis_status = Thesis.objects.filter(student=student).first()
    total_reports = ProgressReport.objects.filter(student=student).count()
    total_meetings = Meeting.objects.filter(student=student).count()
    pending_reports = ProgressReport.objects.filter(student=student, status='Submitted').count()
    
    # Recent items (LIMITED to 5)
    recent_synopses = Synopsis.objects.filter(student=student).order_by('-submission_date')[:5]
    recent_theses = Thesis.objects.filter(student=student).order_by('-submission_date')[:5]
    recent_meetings = Meeting.objects.filter(student=student).order_by('-meeting_date')[:5]
    recent_extensions = ExtensionCase.objects.filter(student=student).order_by('-request_date')[:5]
    
    # Upcoming meetings (future only)
    upcoming_meetings = Meeting.objects.filter(
        student=student,
        meeting_date__gte=timezone.now()
    ).order_by('meeting_date')[:5]
    
    # Notifications
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    
    context = {
        'student': student,
        'synopsis': recent_synopses.first(),
        'thesis': recent_theses.first(),
        'total_reports': total_reports,
        'pending_reports': pending_reports,
        'total_meetings': total_meetings,
        'recent_synopses': recent_synopses,
        'recent_theses': recent_theses,
        'recent_meetings': recent_meetings,
        'recent_extensions': recent_extensions,
        'upcoming_meetings': upcoming_meetings,
        'unread_notifications': unread_notifications,
        'unread_count': unread_count,
    }
    return render(request, 'student/dashboard.html', context)


# ======================
# STUDENT SYNOPSIS
# ======================
@login_required
def student_synopsis_list(request):
    student = get_object_or_404(Student, user=request.user)
    synopses = Synopsis.objects.filter(student=student)
    
    search_query = request.GET.get('search', '')
    if search_query:
        synopses = synopses.filter(title__icontains=search_query)
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        synopses = synopses.filter(status=status_filter)
    
    synopses = synopses.order_by('-submission_date')
    
    return render(request, 'student/synopsis/list.html', {
        'synopses': synopses,
        'search_query': search_query,
        'status_filter': status_filter,
    })


@login_required
def student_synopsis_create(request):
    student = get_object_or_404(Student, user=request.user)
    if request.method == 'POST':
        title = request.POST.get('title')
        file = request.FILES.get('file')
        if not title or not file:
            messages.error(request, 'Please fill all fields.')
            return redirect('student_synopsis_create')
        if not file.name.endswith('.pdf'):
            messages.error(request, 'Only PDF files are allowed.')
            return redirect('student_synopsis_create')
        max_size = 5 * 1024 * 1024
        if file.size > max_size:
            messages.error(request, 'File size must be less than 5MB.')
            return redirect('student_synopsis_create')
        synopsis = Synopsis.objects.create(
            student=student,
            title=title,
            document=file,
            status='Pending'
        )
        if student.supervisor:
            Notification.objects.create(
                user=student.supervisor.user,
                notification_type='System',
                message=f'New synopsis submitted by {student.user.get_full_name()}',
                link=f'/supervisor/synopsis/{synopsis.id}/'
            )
        messages.success(request, 'Synopsis submitted successfully!')
        return redirect('student_synopsis_list')
    return render(request, 'student/synopsis/create.html')


@login_required
def student_synopsis_detail(request, pk):
    synopsis = get_object_or_404(Synopsis, pk=pk, student__user=request.user)
    return render(request, 'student/synopsis/detail.html', {'synopsis': synopsis})


@login_required
def student_synopsis_submit(request):
    student = get_object_or_404(Student, user=request.user)
    if request.method == 'POST':
        form = SynopsisSubmitForm(request.POST, request.FILES)
        if form.is_valid():
            synopsis = form.save(commit=False)
            synopsis.student = student
            synopsis.status = 'submitted'
            synopsis.save()
            if student.supervisor:
                Notification.objects.create(
                    user=student.supervisor.user,
                    notification_type='System',
                    message=f"{student.user.get_full_name()} has submitted a synopsis: {synopsis.title}",
                    link=f"/supervisor/synopsis/{synopsis.id}/"
                )
            messages.success(request, "Synopsis submitted successfully!")
            return redirect('student_synopsis_list')
    else:
        form = SynopsisSubmitForm()
    return render(request, 'student/synopsis/submit.html', {'form': form})


@login_required
def student_synopsis_resubmit(request, pk):
    old_synopsis = get_object_or_404(Synopsis, pk=pk, student__user=request.user)
    if old_synopsis.status != 'changes_requested':
        messages.error(request, "You cannot resubmit this synopsis.")
        return redirect('student_synopsis_list')
    
    if request.method == 'POST':
        form = SynopsisSubmitForm(request.POST, request.FILES)
        if form.is_valid():
            new_synopsis = form.save(commit=False)
            new_synopsis.student = old_synopsis.student
            new_synopsis.status = 'submitted'
            new_synopsis.version = old_synopsis.version + 1
            new_synopsis.previous_version = old_synopsis
            new_synopsis.save()
            if old_synopsis.student.supervisor:
                Notification.objects.create(
                    user=old_synopsis.student.supervisor.user,
                    notification_type='System',
                    message=f"{old_synopsis.student.user.get_full_name()} has resubmitted their synopsis.",
                    link=f"/supervisor/synopsis/{new_synopsis.id}/"
                )
            messages.success(request, "Synopsis resubmitted successfully!")
            return redirect('student_synopsis_list')
    else:
        form = SynopsisSubmitForm(initial={'title': old_synopsis.title})
    return render(request, 'student/synopsis/resubmit.html', {'form': form, 'old_synopsis': old_synopsis})


# ======================
# STUDENT THESIS
# ======================
@login_required
def student_thesis_list(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found. Please contact admin.")
        return redirect('student_dashboard')
    
    theses = Thesis.objects.filter(student=student).order_by('-submission_date')
    return render(request, 'student/thesis/list.html', {'theses': theses})


@login_required
def student_thesis_create(request):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found. Please contact admin.")
        return redirect('student_dashboard')
    
    if request.method == 'POST':
        title = request.POST.get('title')
        file = request.FILES.get('file')
        if not title or not file:
            messages.error(request, 'Please fill all fields.')
            return redirect('student_thesis_create')
        if not file.name.endswith('.pdf'):
            messages.error(request, 'Only PDF files are allowed.')
            return redirect('student_thesis_create')
        thesis = Thesis.objects.create(
            student=student,
            title=title,
            file=file,
            status='Submitted'
        )
        if student.supervisor:
            Notification.objects.create(
                user=student.supervisor.user,
                notification_type='System',
                message=f'New thesis submitted by {student.user.get_full_name()}',
                link=f'/supervisor/thesis/{thesis.id}/'
            )
        messages.success(request, 'Thesis submitted successfully!')
        return redirect('student_thesis_list')
    return render(request, 'student/thesis/create.html')


@login_required
def student_thesis_detail(request, pk):
    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found. Please contact admin.")
        return redirect('student_dashboard')
    
    thesis = get_object_or_404(Thesis, pk=pk, student__user=request.user)
    return render(request, 'student/thesis/detail.html', {'thesis': thesis})


# ======================
# STUDENT PROGRESS REPORTS
# ======================
@login_required
def student_progress_list(request):
    student = get_object_or_404(Student, user=request.user)
    reports = ProgressReport.objects.filter(student=student).order_by('-submission_date')
    return render(request, 'student/progress/list.html', {'reports': reports})


# ========== UPDATED STUDENT PROGRESS CREATE VIEW (using form) ==========
@login_required
def student_progress_create(request):
    student = get_object_or_404(Student, user=request.user)
    if request.method == 'POST':
        form = ProgressReportSubmitForm(request.POST, request.FILES)
        if form.is_valid():
            report = form.save(commit=False)
            report.student = student
            report.status = 'Submitted'
            report.save()
            # Notify supervisor
            if student.supervisor:
                Notification.objects.create(
                    user=student.supervisor.user,
                    notification_type='System',
                    message=f"New progress report submitted by {student.user.get_full_name()} for semester {report.semester}",
                    link=f"/supervisor/progress/{report.id}/review/"
                )
            messages.success(request, 'Progress report submitted successfully!')
            return redirect('student_progress_list')
    else:
        form = ProgressReportSubmitForm()
    return render(request, 'student/progress/create.html', {'form': form})


@login_required
def student_progress_detail(request, pk):
    report = get_object_or_404(ProgressReport, pk=pk, student__user=request.user)
    return render(request, 'student/progress/detail.html', {'report': report})


# ======================
# STUDENT MEETINGS
# ======================
@login_required
def student_meeting_list(request):
    student = get_object_or_404(Student, user=request.user)
    meetings = Meeting.objects.filter(student=student).order_by('-meeting_date')
    return render(request, 'student/meeting/list.html', {'meetings': meetings})


@login_required
def student_meeting_detail(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk, student__user=request.user)
    return render(request, 'student/meeting/detail.html', {'meeting': meeting})


# ======================
# STUDENT EXTENSIONS (UPDATED)
# ======================

@login_required
def student_extension_list(request):
    student = get_object_or_404(Student, user=request.user)
    extensions = ExtensionCase.objects.filter(student=student).order_by('-request_date')
    return render(request, 'student/extension/list.html', {'extensions': extensions})


@login_required
def student_extension_create(request):
    student = get_object_or_404(Student, user=request.user)
    if request.method == 'POST':
        form = ExtensionRequestForm(request.POST, request.FILES)
        if form.is_valid():
            extension = form.save(commit=False)
            extension.student = student
            extension.save()
            # Notify supervisor
            if student.supervisor:
                Notification.objects.create(
                    user=student.supervisor.user,
                    notification_type='System',
                    message=f"Extension request submitted by {student.user.get_full_name()}",
                    link=reverse('supervisor_extension_detail', args=[extension.id])
                )
            messages.success(request, "Extension request submitted successfully.")
            return redirect('student_extension_list')
    else:
        form = ExtensionRequestForm()
    return render(request, 'student/extension/create.html', {'form': form})


@login_required
def student_extension_detail(request, pk):
    extension = get_object_or_404(ExtensionCase, pk=pk, student__user=request.user)
    return render(request, 'student/extension/detail.html', {'extension': extension})


# ======================
# STUDENT DEGREE LETTER (UPDATED)
# ======================
@login_required
def student_degree_request(request):
    student = get_object_or_404(Student, user=request.user)
    degree = DegreeLetter.objects.filter(student=student).first()
    if request.method == 'POST':
        if degree:
            messages.info(request, 'You have already requested a degree letter.')
        else:
            degree = DegreeLetter.objects.create(student=student, verification_status='Pending')
            # Notify admin
            admin_users = User.objects.filter(is_superuser=True)
            for admin in admin_users:
                Notification.objects.create(
                    user=admin,
                    notification_type='System',
                    message=f"Degree letter requested by {student.user.get_full_name()}",
                    link=reverse('admin_degree_detail', args=[degree.id])
                )
            messages.success(request, 'Degree letter requested successfully!')
        return redirect('student_degree_request')
    return render(request, 'student/degree/request.html', {'degree': degree})


# ======================
# STUDENT PROFILE
# ======================
@login_required
def student_profile_update(request):
    student = get_object_or_404(Student, user=request.user)
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        if hasattr(student, 'phone'):
            student.phone = request.POST.get('phone', '')
        student.save()
        messages.success(request, 'Profile updated successfully!')
        return redirect('student_dashboard')
    return render(request, 'student/profile/update.html', {'student': student})


@login_required
def student_change_password(request):
    if request.method == 'POST':
        old = request.POST.get('old_password')
        new1 = request.POST.get('new_password1')
        new2 = request.POST.get('new_password2')
        if not request.user.check_password(old):
            messages.error(request, 'Old password is incorrect.')
        elif new1 != new2:
            messages.error(request, 'New passwords do not match.')
        elif len(new1) < 6:
            messages.error(request, 'Password must be at least 6 characters.')
        else:
            request.user.set_password(new1)
            request.user.save()
            messages.success(request, 'Password changed successfully! Please login again.')
            return redirect('login')
    return render(request, 'student/profile/change_password.html')


# =================================================
# ADMIN STUDENT MANAGEMENT
# =================================================
@login_required
@user_passes_test(is_admin)
def admin_student_list(request):
    students = Student.objects.select_related('user', 'supervisor').all()
    return render(request, 'admin/student/list.html', {'students': students})


@login_required
@user_passes_test(is_admin)
def admin_student_create(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists')
            return redirect('admin_student_create')
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        group, _ = Group.objects.get_or_create(name='Student')
        user.groups.add(group)
        student = Student.objects.create(
            user=user,
            registration_no=request.POST.get('registration_no'),
            department=request.POST.get('department'),
            session=request.POST.get('session'),
            program=request.POST.get('program'),
            enrollment_status=request.POST.get('enrollment_status', 'Active'),
            admission_date=request.POST.get('admission_date') or timezone.now().date()
        )
        supervisor_id = request.POST.get('supervisor')
        if supervisor_id:
            student.supervisor_id = supervisor_id
            student.save()
        messages.success(request, 'Student created successfully!')
        return redirect('admin_student_list')
    supervisors = Supervisor.objects.all()
    return render(request, 'admin/student/create.html', {'supervisors': supervisors})


@login_required
@user_passes_test(is_admin)
def admin_student_detail(request, pk):
    student = get_object_or_404(Student, pk=pk)
    return render(request, 'admin/student/detail.html', {'student': student})


@login_required
@user_passes_test(is_admin)
def admin_student_update(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        user = student.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        student.registration_no = request.POST.get('registration_no', student.registration_no)
        student.department = request.POST.get('department', student.department)
        student.session = request.POST.get('session', student.session)
        student.program = request.POST.get('program', student.program)
        student.enrollment_status = request.POST.get('enrollment_status', student.enrollment_status)
        student.supervisor_id = request.POST.get('supervisor') or None
        student.save()
        messages.success(request, 'Student updated successfully!')
        return redirect('admin_student_list')
    supervisors = Supervisor.objects.all()
    return render(request, 'admin/student/update.html', {'student': student, 'supervisors': supervisors})


@login_required
@user_passes_test(is_admin)
def admin_student_delete(request, pk):
    student = get_object_or_404(Student, pk=pk)
    if request.method == 'POST':
        user = student.user
        student.delete()
        user.delete()
        messages.success(request, 'Student deleted successfully!')
        return redirect('admin_student_list')
    return render(request, 'admin/student/delete.html', {'student': student})


# =================================================
# ADMIN SUPERVISOR MANAGEMENT
# =================================================
@login_required
@user_passes_test(is_admin)
def admin_supervisor_list(request):
    supervisors = Supervisor.objects.select_related('user').all()
    return render(request, 'admin/supervisor/list.html', {'supervisors': supervisors})


@login_required
@user_passes_test(is_admin)
def admin_supervisor_create(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, f'Username "{username}" already exists. Please choose a different username.')
            return redirect('admin_supervisor_create')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        group, _ = Group.objects.get_or_create(name='Supervisor')
        user.groups.add(group)
        
        emp_id = request.POST.get('employee_id')
        if emp_id == '' or emp_id == 'None' or emp_id is None:
            emp_id = None
        
        max_students = request.POST.get('max_students')
        if max_students and max_students.isdigit():
            max_students = int(max_students)
        else:
            max_students = 5
        
        supervisor = Supervisor.objects.create(
            user=user,
            employee_id=emp_id,
            department=request.POST.get('department'),
            designation=request.POST.get('designation'),
            availability_status=request.POST.get('availability_status', 'Available'),
            max_students=max_students
        )
        messages.success(request, 'Supervisor created successfully!')
        return redirect('admin_supervisor_list')
    
    return render(request, 'admin/supervisor/create.html')


@login_required
@user_passes_test(is_admin)
def admin_supervisor_detail(request, pk):
    supervisor = get_object_or_404(Supervisor, pk=pk)
    students = Student.objects.filter(supervisor=supervisor)
    return render(request, 'admin/supervisor/detail.html', {'supervisor': supervisor, 'students': students})


@login_required
@user_passes_test(is_admin)
def admin_supervisor_update(request, pk):
    supervisor = get_object_or_404(Supervisor, pk=pk)
    if request.method == 'POST':
        user = supervisor.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.save()
        
        emp_id = request.POST.get('employee_id')
        if emp_id == '' or emp_id == 'None' or emp_id is None:
            supervisor.employee_id = None
        else:
            supervisor.employee_id = emp_id
        
        supervisor.department = request.POST.get('department', supervisor.department)
        supervisor.designation = request.POST.get('designation', supervisor.designation)
        supervisor.availability_status = request.POST.get('availability_status', supervisor.availability_status)
        
        max_students = request.POST.get('max_students')
        if max_students and max_students.isdigit():
            supervisor.max_students = int(max_students)
        else:
            supervisor.max_students = 5
        
        supervisor.save()
        messages.success(request, 'Supervisor updated successfully!')
        return redirect('admin_supervisor_list')
    
    return render(request, 'admin/supervisor/update.html', {'supervisor': supervisor})


@login_required
@user_passes_test(is_admin)
def admin_supervisor_delete(request, pk):
    supervisor = get_object_or_404(Supervisor, pk=pk)
    if request.method == 'POST':
        user = supervisor.user
        supervisor.delete()
        user.delete()
        messages.success(request, 'Supervisor deleted successfully!')
        return redirect('admin_supervisor_list')
    return render(request, 'admin/supervisor/delete.html', {'supervisor': supervisor})


# =================================================
# ADMIN SYNOPSIS MANAGEMENT
# =================================================
@login_required
@user_passes_test(is_admin)
def admin_synopsis_list(request):
    synopses = Synopsis.objects.select_related('student', 'supervisor').all().order_by('-submission_date')
    return render(request, 'admin/synopsis/list.html', {'synopses': synopses})


@login_required
@user_passes_test(is_admin)
def admin_synopsis_detail(request, pk):
    synopsis = get_object_or_404(Synopsis, pk=pk)
    return render(request, 'admin/synopsis/detail.html', {'synopsis': synopsis})


@login_required
@user_passes_test(is_admin)
def admin_synopsis_assign(request, pk):
    synopsis = get_object_or_404(Synopsis, pk=pk)
    if request.method == 'POST':
        supervisor_id = request.POST.get('supervisor')
        synopsis.supervisor_id = supervisor_id
        synopsis.status = 'Assigned'
        synopsis.save()
        messages.success(request, 'Supervisor assigned successfully!')
        return redirect('admin_synopsis_list')
    supervisors = Supervisor.objects.filter(availability_status='Available')
    return render(request, 'admin/synopsis/assign.html', {'synopsis': synopsis, 'supervisors': supervisors})


@login_required
@user_passes_test(is_admin)
def admin_synopsis_approve(request, pk):
    synopsis = get_object_or_404(Synopsis, pk=pk)
    if request.method == 'POST':
        synopsis.status = 'Approved'
        synopsis.remarks = request.POST.get('remarks', '')
        synopsis.save()
        messages.success(request, 'Synopsis approved!')
        return redirect('admin_synopsis_list')
    return redirect('admin_synopsis_detail', pk=pk)


@login_required
@user_passes_test(is_admin)
def admin_synopsis_reject(request, pk):
    synopsis = get_object_or_404(Synopsis, pk=pk)
    if request.method == 'POST':
        synopsis.status = 'Rejected'
        synopsis.remarks = request.POST.get('remarks', '')
        synopsis.save()
        messages.success(request, 'Synopsis rejected!')
        return redirect('admin_synopsis_list')
    return redirect('admin_synopsis_detail', pk=pk)


# =================================================
# ADMIN THESIS MANAGEMENT
# =================================================
@login_required
@user_passes_test(is_admin)
def admin_thesis_list(request):
    theses = Thesis.objects.select_related('student').all().order_by('-submission_date')
    return render(request, 'admin/thesis/list.html', {'theses': theses})


@login_required
@user_passes_test(is_admin)
def admin_thesis_detail(request, pk):
    thesis = get_object_or_404(Thesis, pk=pk)
    evaluations = thesis.evaluations.all()
    context = {
        'thesis': thesis,
        'evaluations': evaluations,
    }
    return render(request, 'admin/thesis/detail.html', context)


@login_required
@user_passes_test(is_admin)
def admin_thesis_assign_examiners(request, pk):
    thesis = get_object_or_404(Thesis, pk=pk)
    if request.method == 'POST':
        form = ThesisAssignmentForm(request.POST, thesis=thesis)
        if form.is_valid():
            internal = form.cleaned_data['internal_examiner']
            external = form.cleaned_data['external_examiner']
            if internal:
                ThesisEvaluation.objects.get_or_create(thesis=thesis, examiner=internal, defaults={'submitted': False})
            if external:
                ThesisEvaluation.objects.get_or_create(thesis=thesis, examiner=external, defaults={'submitted': False})
            messages.success(request, "Examiners assigned successfully.")
            return redirect('admin_thesis_detail', pk=thesis.id)
    else:
        form = ThesisAssignmentForm(thesis=thesis)
    return render(request, 'admin/thesis/assign_examiners.html', {'form': form, 'thesis': thesis})


@login_required
@user_passes_test(is_admin)
def admin_thesis_record_viva(request, pk):
    thesis = get_object_or_404(Thesis, pk=pk)
    if request.method == 'POST':
        form = VivaResultForm(request.POST, instance=thesis)
        if form.is_valid():
            thesis = form.save(commit=False)
            if thesis.status == 'Accepted':
                thesis.final_decision_date = timezone.now()
            thesis.save()
            messages.success(request, "Viva result recorded.")
            return redirect('admin_thesis_detail', pk=thesis.id)
    else:
        form = VivaResultForm(instance=thesis)
    return render(request, 'admin/thesis/viva_form.html', {'form': form, 'thesis': thesis})


@login_required
@user_passes_test(is_admin)
def admin_thesis_finalize(request, pk):
    thesis = get_object_or_404(Thesis, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['Accepted', 'Rejected']:
            thesis.status = new_status
            thesis.final_decision_date = timezone.now()
            thesis.save()
            # Notify student
            Notification.objects.create(
                user=thesis.student.user,
                notification_type='System',
                message=f"Your thesis has been {new_status}.",
                link=reverse('student_thesis_detail', args=[thesis.id])
            )
            messages.success(request, f"Thesis {new_status}.")
        return redirect('admin_thesis_detail', pk=thesis.id)
    return render(request, 'admin/thesis/finalize.html', {'thesis': thesis})


@login_required
@user_passes_test(is_admin)
def admin_thesis_update_status(request, pk):
    thesis = get_object_or_404(Thesis, pk=pk)
    if request.method == 'POST':
        thesis.status = request.POST.get('status', thesis.status)
        thesis.remarks = request.POST.get('remarks', '')
        thesis.save()
        messages.success(request, 'Thesis status updated!')
        return redirect('admin_thesis_list')
    return redirect('admin_thesis_detail', pk=pk)


# =================================================
# ADMIN PROGRESS REPORTS MANAGEMENT
# =================================================
@login_required
@user_passes_test(is_admin)
def admin_progress_list(request):
    reports = ProgressReport.objects.select_related('student').all().order_by('-submission_date')
    return render(request, 'admin/progress/list.html', {'reports': reports})


@login_required
@user_passes_test(is_admin)
def admin_progress_detail(request, pk):
    report = get_object_or_404(ProgressReport, pk=pk)
    return render(request, 'admin/progress/detail.html', {'report': report})


# =================================================
# ADMIN MEETINGS MANAGEMENT
# =================================================
@login_required
@user_passes_test(is_admin)
def admin_meeting_list(request):
    meetings = Meeting.objects.select_related('student', 'supervisor').all().order_by('-meeting_date')
    return render(request, 'admin/meeting/list.html', {'meetings': meetings})


@login_required
@user_passes_test(is_admin)
def admin_meeting_detail(request, pk):
    meeting = get_object_or_404(Meeting, pk=pk)
    return render(request, 'admin/meeting/detail.html', {'meeting': meeting})


# =================================================
# ADMIN EXTENSIONS MANAGEMENT
# =================================================
@login_required
@user_passes_test(is_admin)
def admin_extension_list(request):
    extensions = ExtensionCase.objects.select_related('student').all().order_by('-request_date')
    return render(request, 'admin/extension/list.html', {'extensions': extensions})


@login_required
@user_passes_test(is_admin)
def admin_extension_detail(request, pk):
    extension = get_object_or_404(ExtensionCase, pk=pk)
    return render(request, 'admin/extension/detail.html', {'extension': extension})


@login_required
@user_passes_test(is_admin)
def admin_extension_approve(request, pk):
    extension = get_object_or_404(ExtensionCase, pk=pk)
    if request.method == 'POST':
        extension.status = 'Approved'
        extension.remarks = request.POST.get('remarks', '')
        extension.approval_date = timezone.now().date()
        extension.save()
        messages.success(request, 'Extension approved!')
        return redirect('admin_extension_list')
    return redirect('admin_extension_detail', pk=pk)


@login_required
@user_passes_test(is_admin)
def admin_extension_reject(request, pk):
    extension = get_object_or_404(ExtensionCase, pk=pk)
    if request.method == 'POST':
        extension.status = 'Rejected'
        extension.remarks = request.POST.get('remarks', '')
        extension.save()
        messages.success(request, 'Extension rejected!')
        return redirect('admin_extension_list')
    return redirect('admin_extension_detail', pk=pk)


# =================================================
# ADMIN DEGREE LETTER MANAGEMENT (NEW)
# =================================================

@login_required
@user_passes_test(is_admin)
def admin_degree_list(request):
    degrees = DegreeLetter.objects.select_related('student', 'student__user').order_by('-request_date')
    return render(request, 'admin/degree/list.html', {'degrees': degrees})


@login_required
@user_passes_test(is_admin)
def admin_degree_detail(request, pk):
    degree = get_object_or_404(DegreeLetter, pk=pk)
    return render(request, 'admin/degree/detail.html', {'degree': degree})


@login_required
@user_passes_test(is_admin)
def admin_degree_verify(request, pk):
    degree = get_object_or_404(DegreeLetter, pk=pk)
    if request.method == 'POST':
        form = DegreeLetterVerificationForm(request.POST, instance=degree)
        if form.is_valid():
            degree = form.save(commit=False)
            degree.verified_by = request.user.supervisor_profile if hasattr(request.user, 'supervisor_profile') else None
            degree.save()
            # Notify student
            Notification.objects.create(
                user=degree.student.user,
                notification_type='System',
                message=f"Your degree letter request has been {degree.verification_status}.",
                link=reverse('student_degree_request')
            )
            messages.success(request, f"Degree request {degree.verification_status}.")
            return redirect('admin_degree_detail', pk=degree.id)
    else:
        form = DegreeLetterVerificationForm(instance=degree)
    return render(request, 'admin/degree/verify.html', {'form': form, 'degree': degree})


from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import io

@login_required
@user_passes_test(is_admin)
def admin_degree_issue(request, pk):
    degree = get_object_or_404(DegreeLetter, pk=pk)
    if degree.verification_status != 'Verified':
        messages.error(request, "Only verified requests can be issued.")
        return redirect('admin_degree_detail', pk=degree.id)

    # Generate PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    title_style = styles['Title']
    title_style.alignment = 1  # center
    elements.append(Paragraph("DEGREE COMPLETION LETTER", title_style))
    elements.append(Spacer(1, 0.5*inch))

    # Date
    from datetime import date
    elements.append(Paragraph(f"Date: {date.today().strftime('%B %d, %Y')}", styles['Normal']))
    elements.append(Spacer(1, 0.3*inch))

    # Student details
    student = degree.student
    data = [
        ["Student Name:", student.user.get_full_name()],
        ["Registration No:", student.registration_no],
        ["Program:", student.program],
        ["Department:", student.department],
        ["Session:", student.session],
        ["CGPA / Result:", "3.8 / 4.0 (Example)"],  # TODO: Fetch actual data if available
    ]
    table = Table(data, colWidths=[1.5*inch, 4*inch])
    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('BACKGROUND', (0,0), (0,-1), colors.lightgrey),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 0.3*inch))

    # Body
    body_text = f"""
    This is to certify that <b>{student.user.get_full_name()}</b> has successfully completed all requirements
    for the degree of <b>{student.program}</b> in <b>{student.department}</b> during the session <b>{student.session}</b>.
    The student has demonstrated outstanding performance and is hereby awarded the degree.
    """
    elements.append(Paragraph(body_text, styles['Normal']))
    elements.append(Spacer(1, 0.5*inch))

    # Signatures
    sig_data = [
        ["______________________", "______________________"],
        ["Dean / Head of Department", "Registrar"]
    ]
    sig_table = Table(sig_data, colWidths=[3*inch, 3*inch])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
    ]))
    elements.append(sig_table)

    doc.build(elements)
    pdf = buffer.getvalue()
    buffer.close()

    # Save the PDF file to model
    from django.core.files.base import ContentFile
    filename = f"degree_{student.registration_no}.pdf"
    degree.letter_file.save(filename, ContentFile(pdf))
    degree.issue_date = date.today()
    degree.verification_status = 'Issued'
    degree.save()

    # Notify student
    Notification.objects.create(
        user=degree.student.user,
        notification_type='System',
        message="Your degree letter has been issued and is ready for download.",
        link=reverse('student_degree_request')
    )

    messages.success(request, "Degree letter issued successfully.")
    return redirect('admin_degree_detail', pk=degree.id)


# =================================================
# EXAMINER VIEWS
# =================================================

@login_required
def examiner_dashboard(request):
    try:
        examiner = Examiner.objects.get(user=request.user)
    except Examiner.DoesNotExist:
        messages.error(request, "Examiner profile not found.")
        return redirect('home')
    
    assigned_evaluations = ThesisEvaluation.objects.filter(examiner=examiner, submitted=False)
    submitted_evaluations = ThesisEvaluation.objects.filter(examiner=examiner, submitted=True)
    
    context = {
        'examiner': examiner,
        'assigned_evaluations': assigned_evaluations,
        'submitted_evaluations': submitted_evaluations,
    }
    return render(request, 'examiner/dashboard.html', context)


@login_required
def examiner_thesis_detail(request, pk):
    evaluation = get_object_or_404(ThesisEvaluation, pk=pk, examiner__user=request.user)
    thesis = evaluation.thesis
    return render(request, 'examiner/thesis_detail.html', {'evaluation': evaluation, 'thesis': thesis})


@login_required
def examiner_evaluation_submit(request, pk):
    evaluation = get_object_or_404(ThesisEvaluation, pk=pk, examiner__user=request.user)
    if evaluation.submitted:
        messages.warning(request, "You have already submitted your evaluation.")
        return redirect('examiner_dashboard')
    
    if request.method == 'POST':
        form = ExaminerReportForm(request.POST, request.FILES, instance=evaluation)
        if form.is_valid():
            evaluation = form.save(commit=False)
            evaluation.submitted = True
            evaluation.submitted_at = timezone.now()
            evaluation.save()
            # Notify admin
            admin_users = User.objects.filter(is_superuser=True)
            for admin in admin_users:
                Notification.objects.create(
                    user=admin,
                    notification_type='System',
                    message=f"Evaluation submitted by {evaluation.examiner.name} for thesis: {evaluation.thesis.title}",
                    link=reverse('admin_thesis_detail', args=[evaluation.thesis.id])
                )
            messages.success(request, "Evaluation submitted successfully.")
            return redirect('examiner_dashboard')
    else:
        form = ExaminerReportForm(instance=evaluation)
    return render(request, 'examiner/evaluation_form.html', {'form': form, 'evaluation': evaluation})


# =================================================
# NOTIFICATION MANAGEMENT (COMMON)
# =================================================
@login_required
def mark_all_read(request):
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
    messages.success(request, "All notifications marked as read.")
    return redirect(request.META.get('HTTP_REFERER', 'student_dashboard'))


@login_required
def all_notifications(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'notifications/list.html', {'notifications': notifications})


# =================================================
# SUPERVISOR PROGRESS REPORTS MANAGEMENT
# =================================================
@login_required
def supervisor_progress_list(request):
    supervisor = get_object_or_404(Supervisor, user=request.user)
    reports = ProgressReport.objects.filter(student__supervisor=supervisor).order_by('-submission_date')
    
    search_query = request.GET.get('search', '')
    if search_query:
        reports = reports.filter(
            Q(student__user__first_name__icontains=search_query) |
            Q(student__user__last_name__icontains=search_query) |
            Q(semester__icontains=search_query)
        )
    
    status_filter = request.GET.get('status', '')
    if status_filter:
        reports = reports.filter(status=status_filter)
    
    context = {
        'reports': reports,
        'search_query': search_query,
        'status_filter': status_filter,
        'status_choices': ProgressReport.REPORT_STATUS,
    }
    return render(request, 'supervisor/progress/list.html', context)


@login_required
def supervisor_progress_review(request, pk):
    report = get_object_or_404(ProgressReport, pk=pk)
    supervisor = get_object_or_404(Supervisor, user=request.user)
    
    if report.student.supervisor != supervisor:
        messages.error(request, "You are not authorized to review this report.")
        return redirect('supervisor_dashboard')
    
    if request.method == 'POST':
        form = ProgressReportReviewForm(request.POST, instance=report)
        if form.is_valid():
            report = form.save(commit=False)
            report.reviewed_by = supervisor
            report.reviewed_at = timezone.now()
            report.save()
            
            Notification.objects.create(
                user=report.student.user,
                notification_type='System',
                message=f"Your progress report for {report.semester} has been {report.get_status_display()}.",
                link=f"/student/progress/{report.id}/"
            )
            messages.success(request, "Review submitted successfully.")
            return redirect('supervisor_progress_list')
    else:
        form = ProgressReportReviewForm(instance=report)
    
    return render(request, 'supervisor/progress/review.html', {'form': form, 'report': report})


@login_required
def supervisor_progress_detail(request, pk):
    report = get_object_or_404(ProgressReport, pk=pk)
    supervisor = get_object_or_404(Supervisor, user=request.user)
    
    if report.student.supervisor != supervisor:
        messages.error(request, "You are not authorized to view this report.")
        return redirect('supervisor_dashboard')
    
    return render(request, 'supervisor/progress/detail.html', {'report': report})