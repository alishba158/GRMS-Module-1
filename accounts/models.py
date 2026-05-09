from django.db import models
from django.contrib.auth.models import User
from django.core.validators import FileExtensionValidator
from django.utils import timezone

# ===== User Roles =====
class UserProfile(models.Model):
    USER_ROLES = (
        ('Student', 'Student'),
        ('Supervisor', 'Supervisor'),
        ('Admin', 'Admin'),
        ('Coordinator', 'Department Coordinator'),
        ('Examiner', 'Examiner'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=USER_ROLES, default='Student')
    phone_no = models.CharField(max_length=15, blank=True, null=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.role}"


# ===== Student Model =====
class Student(models.Model):
    ENROLLMENT_STATUS = (
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Completed', 'Completed'),
        ('Withdrawn', 'Withdrawn'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    registration_no = models.CharField(max_length=30, unique=True)
    department = models.CharField(max_length=100)
    session = models.CharField(max_length=20)
    program = models.CharField(max_length=50)
    enrollment_status = models.CharField(max_length=20, choices=ENROLLMENT_STATUS, default='Active')
    admission_date = models.DateField(default=timezone.now)
    supervisor = models.ForeignKey('Supervisor', on_delete=models.SET_NULL, null=True, blank=True, related_name='students')
    
    def __str__(self):
        return f"{self.registration_no} - {self.user.get_full_name()}"


# ===== Supervisor Model =====
class Supervisor(models.Model):
    AVAILABILITY = (
        ('Available', 'Available'),
        ('Not Available', 'Not Available'),
        ('On Leave', 'On Leave'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='supervisor_profile')
    employee_id = models.CharField(max_length=30, unique=True, blank=True, null=True)
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=50)
    availability_status = models.CharField(max_length=20, choices=AVAILABILITY, default='Available')
    max_students = models.IntegerField(default=5)
    
    def __str__(self):
        return f"Prof. {self.user.get_full_name()} - {self.department}"


# ===== Examiner Model (Fixed email length) =====
class Examiner(models.Model):
    EXAMINER_TYPE = (
        ('Internal', 'Internal'),
        ('External', 'External'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='examiner_profile', null=True, blank=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, max_length=250)   # ← max_length reduced to 250
    phone_no = models.CharField(max_length=15)
    designation = models.CharField(max_length=50)
    examiner_type = models.CharField(max_length=20, choices=EXAMINER_TYPE)
    institution = models.CharField(max_length=100)
    area_of_expertise = models.CharField(max_length=150)
    availability_status = models.CharField(max_length=20, choices=Supervisor.AVAILABILITY, default='Available')
    
    def __str__(self):
        return f"{self.name} - {self.examiner_type}"


# ===== Synopsis Model (Merged with versioning & review) =====
class Synopsis(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under Review'),
        ('changes_requested', 'Changes Requested'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='synopses')
    title = models.CharField(max_length=300)
    document = models.FileField(upload_to='synopses/', validators=[FileExtensionValidator(['pdf'])])
    submission_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Supervisor assigned (optional)
    supervisor = models.ForeignKey(Supervisor, on_delete=models.SET_NULL, null=True, blank=True, related_name='synopses')
    
    # Review fields
    reviewed_by = models.ForeignKey(Supervisor, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_synopses')
    review_comments = models.TextField(blank=True, null=True)   # null=True add kiya
    review_date = models.DateTimeField(null=True, blank=True)
    
    # Versioning
    version = models.IntegerField(default=1)
    previous_version = models.ForeignKey('Synopsis', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Resubmission deadline (agar changes requested ho)
    resubmission_deadline = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.title} - {self.student.user.get_full_name()}"


# ===== Progress Report Model =====
class ProgressReport(models.Model):
    REPORT_STATUS = (
        ('Submitted', 'Submitted'),
        ('Under Review', 'Under Review'),
        ('Accepted', 'Accepted'),
        ('Needs Improvement', 'Needs Improvement'),
        ('Rejected', 'Rejected'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='progress_reports')
    semester = models.CharField(max_length=20)
    file = models.FileField(upload_to='research/progress_reports/')
    status = models.CharField(max_length=20, choices=REPORT_STATUS, default='Submitted')
    supervisor_feedback = models.TextField(blank=True, null=True)
    submission_date = models.DateTimeField(auto_now_add=True)
    
    # New fields for review tracking
    reviewed_by = models.ForeignKey(
        'Supervisor', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='progress_reviews'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Report {self.id} - {self.student.registration_no}"


# ===== Thesis Model =====
class Thesis(models.Model):
    THESIS_STATUS = (
        ('Submitted', 'Submitted'),
        ('Under Review', 'Under Review'),
        ('Minor Changes Required', 'Minor Changes Required'),
        ('Major Changes Required', 'Major Changes Required'),
        ('Accepted', 'Accepted'),
        ('Rejected', 'Rejected'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='theses')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='research/theses/')
    status = models.CharField(max_length=25, choices=THESIS_STATUS, default='Submitted')
    submission_date = models.DateTimeField(auto_now_add=True)
    viva_result = models.CharField(max_length=30, blank=True, null=True)
    
    # New field to track final decision date
    final_decision_date = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.title} - {self.student.registration_no}"


# ===== Thesis Evaluation (by examiners) =====
class ThesisEvaluation(models.Model):
    thesis = models.ForeignKey(Thesis, on_delete=models.CASCADE, related_name='evaluations')
    examiner = models.ForeignKey(Examiner, on_delete=models.CASCADE)
    evaluation_date = models.DateField(auto_now_add=True)
    marks = models.IntegerField(null=True, blank=True)  # ← null allowed
    result = models.CharField(max_length=20, blank=True, null=True)  # ← blank allowed
    comments = models.TextField(blank=True, null=True)
    report_file = models.FileField(upload_to='research/evaluation_reports/', blank=True, null=True)
    submitted = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(null=True, blank=True)
    recommendation = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"Evaluation for {self.thesis.title}"


# ===== Meeting Model =====
class Meeting(models.Model):
    MEETING_MODE = (
        ('Online', 'Online'),
        ('In-Person', 'In-Person'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='meetings')
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE, related_name='meetings')
    meeting_date = models.DateTimeField()
    mode = models.CharField(max_length=20, choices=MEETING_MODE)
    agenda = models.TextField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)
    minutes_file = models.FileField(upload_to='research/meetings/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Meeting: {self.student} with {self.supervisor} on {self.meeting_date}"


# ===== Extension Case Model =====
class ExtensionCase(models.Model):
    EXTENSION_STATUS = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='extensions')
    reason = models.TextField()
    requested_duration = models.IntegerField(help_text="Duration in days")
    status = models.CharField(max_length=20, choices=EXTENSION_STATUS, default='Pending')
    supporting_document = models.FileField(upload_to='research/extensions/', blank=True, null=True)
    request_date = models.DateTimeField(auto_now_add=True)
    approval_date = models.DateField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)   # supervisor's remarks when rejecting/approving

    def __str__(self):
        return f"Extension for {self.student.registration_no}"


# ===== Degree Letter Model =====
class DegreeLetter(models.Model):
    VERIFICATION_STATUS = (
        ('Pending', 'Pending Verification'),
        ('Verified', 'Verified'),
        ('Rejected', 'Rejected'),
        ('Issued', 'Issued'),
    )
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='degree_letters')
    request_date = models.DateTimeField(auto_now_add=True)
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='Pending')
    issue_date = models.DateField(blank=True, null=True)
    letter_file = models.FileField(upload_to='degree_letters/', blank=True, null=True)
    verified_by = models.ForeignKey(Supervisor, on_delete=models.SET_NULL, null=True, blank=True)
    remarks = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Degree Letter for {self.student.registration_no}"


# ===== Notification Model =====
class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('System', 'System'),
        ('Email', 'Email'),
        ('Reminder', 'Reminder'),
        ('Alert', 'Alert'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='System')
    message = models.TextField()
    link = models.CharField(max_length=255, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Notification for {self.user.username}"