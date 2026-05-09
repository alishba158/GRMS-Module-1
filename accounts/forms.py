from django import forms
from .models import (
    Synopsis, 
    ProgressReport, 
    Thesis, 
    ThesisEvaluation,
    Examiner,
    ExtensionCase,
    DegreeLetter,
)

# ========== SYNOPSIS MODULE FORMS ==========

class SynopsisSubmitForm(forms.ModelForm):
    class Meta:
        model = Synopsis
        fields = ['title', 'document']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'document': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_document(self):
        doc = self.cleaned_data.get('document')
        if doc:
            if doc.size > 5 * 1024 * 1024:  # 5MB limit
                raise forms.ValidationError("File size must be less than 5MB")
        return doc


class SynopsisReviewForm(forms.ModelForm):
    class Meta:
        model = Synopsis
        fields = ['status', 'review_comments', 'resubmission_deadline']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'review_comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'resubmission_deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['resubmission_deadline'].required = False
        self.fields['status'].choices = [
            ('approved', 'Approve'),
            ('rejected', 'Reject'),
            ('changes_requested', 'Request Changes'),
        ]


# ========== PROGRESS REPORT MODULE FORMS ==========

class ProgressReportSubmitForm(forms.ModelForm):
    class Meta:
        model = ProgressReport
        fields = ['semester', 'file']
        widgets = {
            'semester': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Fall 2025'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file:
            if not file.name.endswith('.pdf'):
                raise forms.ValidationError("Only PDF files are allowed.")
            if file.size > 5 * 1024 * 1024:
                raise forms.ValidationError("File size must be less than 5MB.")
        return file


class ProgressReportReviewForm(forms.ModelForm):
    class Meta:
        model = ProgressReport
        fields = ['status', 'supervisor_feedback']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'supervisor_feedback': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Enter feedback...'}),
        }


# ========== THESIS MODULE FORMS ==========

class ThesisAssignmentForm(forms.Form):
    internal_examiner = forms.ModelChoiceField(
        queryset=Examiner.objects.filter(examiner_type='Internal', availability_status='Available'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    external_examiner = forms.ModelChoiceField(
        queryset=Examiner.objects.filter(examiner_type='External', availability_status='Available'),
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        self.thesis = kwargs.pop('thesis', None)
        super().__init__(*args, **kwargs)
        # Pre-select existing examiners if any
        if self.thesis:
            existing = self.thesis.evaluations.all()
            internal = existing.filter(examiner__examiner_type='Internal').first()
            external = existing.filter(examiner__examiner_type='External').first()
            if internal:
                self.fields['internal_examiner'].initial = internal.examiner
            if external:
                self.fields['external_examiner'].initial = external.examiner


class ExaminerReportForm(forms.ModelForm):
    class Meta:
        model = ThesisEvaluation
        fields = ['marks', 'result', 'recommendation', 'comments', 'report_file']
        widgets = {
            'marks': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'result': forms.Select(attrs={'class': 'form-control'}, choices=[('Pass', 'Pass'), ('Fail', 'Fail')]),
            'recommendation': forms.Select(attrs={'class': 'form-control'}, choices=[
                ('', '-- Select --'),
                ('Accept', 'Accept'),
                ('Minor Changes', 'Minor Changes'),
                ('Major Changes', 'Major Changes'),
                ('Reject', 'Reject')
            ]),
            'comments': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'report_file': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_report_file(self):
        file = self.cleaned_data.get('report_file')
        if file and not file.name.endswith('.pdf'):
            raise forms.ValidationError("Only PDF files are allowed.")
        return file


class VivaResultForm(forms.ModelForm):
    class Meta:
        model = Thesis
        fields = ['viva_result', 'status']
        widgets = {
            'viva_result': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Passed'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
        }


# ========== EXTENSION MODULE FORMS ==========

class ExtensionRequestForm(forms.ModelForm):
    class Meta:
        model = ExtensionCase
        fields = ['reason', 'requested_duration', 'supporting_document']
        widgets = {
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'requested_duration': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'supporting_document': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def clean_requested_duration(self):
        duration = self.cleaned_data.get('requested_duration')
        if duration and duration <= 0:
            raise forms.ValidationError("Duration must be a positive number.")
        return duration
    
    def clean_supporting_document(self):
        doc = self.cleaned_data.get('supporting_document')
        if doc and not doc.name.endswith('.pdf'):
            raise forms.ValidationError("Only PDF files are allowed.")
        return doc


class ExtensionReviewForm(forms.ModelForm):
    class Meta:
        model = ExtensionCase
        fields = ['status', 'remarks']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


# ========== DEGREE LETTER MODULE FORMS ==========

class DegreeLetterRequestForm(forms.ModelForm):
    class Meta:
        model = DegreeLetter
        fields = []  # No fields, just a request button
        # This form is used only to handle POST, no fields needed.


class DegreeLetterVerificationForm(forms.ModelForm):
    class Meta:
        model = DegreeLetter
        fields = ['verification_status', 'remarks']
        widgets = {
            'verification_status': forms.Select(attrs={'class': 'form-control'}),
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }