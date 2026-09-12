from django.db import models
from accounts.models import User, FeeStructure, AcademicSession
from accounts.state import NIGERIA_STATES_AND_LGAS
from django.core.exceptions import ValidationError

class ContactSubmission(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} ({self.email})"
    
class Program(models.Model):
    PROGRAM_TYPE_CHOICES = [
        ('nce', 'NCE'),
        ('diploma', 'Diploma'),
        ('degree', 'Degree'),
    ]

    name = models.CharField(max_length=100)
    program_type = models.CharField(max_length=20, choices=PROGRAM_TYPE_CHOICES, default='nce')
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_program_type_display()})"

    @property
    def screening_fee(self):
        """Return the screening fee based on program type using FeeStructure (applicant fee)"""
        fallback = {
            'degree': 12000.00,
            'diploma': 5000.00,
            'nce': 5000.00,
        }
        try:
            current_session = AcademicSession.objects.filter(is_active=True).first()
            if not current_session:
                return fallback.get(self.program_type, 5000.00)
            # Level names: APP_DEG, APP_ND, APP_NCE (diploma -> ND)
            level_map = {'degree': 'APP_DEG', 'diploma': 'APP_ND', 'nce': 'APP_NCE'}
            level_name = level_map.get(self.program_type, 'APP_NCE')
            screening_fee = FeeStructure.objects.get(
                academic_session=current_session,
                department__name__icontains='screening',
                level__name=level_name,
            )
            return screening_fee.amount
        except (FeeStructure.DoesNotExist, Exception):
            return fallback.get(self.program_type, 5000.00)

class ProgramChoice(models.Model):
    """Model to store program-specific course/department choices"""
    program_type = models.CharField(max_length=20, choices=Program.PROGRAM_TYPE_CHOICES)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['program_type', 'name']
        unique_together = ['program_type', 'name']
    
    def __str__(self):
        return f"{self.get_program_type_display()} - {self.name}"

class ExaminationDetail(models.Model):
    """Model to store examination details for each sitting"""
    EXAM_TYPE_CHOICES = [
        ('waec', 'WAEC'),
        ('neco', 'NECO'),
        ('nabteb', 'NABTEB'),
        ('gce', 'GCE'),
    ]
    
    screening_form = models.ForeignKey('ScreeningForm', on_delete=models.CASCADE, related_name='examination_details')
    sitting = models.CharField(max_length=10, choices=[('first', 'First Sitting'), ('second', 'Second Sitting')])
    exam_type = models.CharField(max_length=10, choices=EXAM_TYPE_CHOICES)
    exam_number = models.CharField(max_length=50)
    exam_year = models.IntegerField()

    class Meta:
        unique_together = ('screening_form', 'sitting')

    def __str__(self):
        return f"{self.screening_form.applicant.user.get_full_name()} - {self.get_sitting_display()} ({self.get_exam_type_display()})"


class ScreeningPayment(models.Model):
    """Model to track screening form payment"""
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    ]
    
    applicant = models.ForeignKey('Applicant', on_delete=models.CASCADE, related_name='screening_payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=2000.00)
    reference = models.CharField(max_length=100, unique=True)
    paystack_reference = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_date = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.applicant.user.get_full_name()} - Screening Payment ({self.get_status_display()})"
    
    @property
    def is_paid(self):
        return self.status == 'success'

class AcademicSubject(models.Model):
    """Model to store individual subject-grade combinations for academic qualifications"""
    SUBJECT_CHOICES = [
        ('english', 'English Language'),
        ('mathematics', 'Mathematics'),
        ('physics', 'Physics'),
        ('chemistry', 'Chemistry'),
        ('biology', 'Biology'),
        ('economics', 'Economics'),
        ('literature', 'Literature in English'),
        ('government', 'Government'),
        ('history', 'History'),
        ('geography', 'Geography'),
        ('commerce', 'Commerce'),
        ('accounting', 'Accounting'),
        ('agriculture', 'Agricultural Science'),
        ('further_maths', 'Further Mathematics'),
        ('civic_education', 'Civic Education'),
        ('christian_religious_studies', 'Christian Religious Studies'),
        ('islamic_studies', 'Islamic Studies'),
        ('yoruba', 'Yoruba'),
        ('hausa', 'Hausa'),
        ('igbo', 'Igbo'),
        ('french', 'French'),
        ('arabic', 'Arabic'),
        ('food_and_nutrition', 'Food and Nutrition'),
        ('home_economics', 'Home Economics'),
        ('technical_drawing', 'Technical Drawing'),
        ('woodwork', 'Woodwork'),
        ('metalwork', 'Metalwork'),
        ('auto_mechanics', 'Auto Mechanics'),
        ('electronics', 'Electronics'),
        ('computer_studies', 'Computer Studies'),
        ('visual_arts', 'Visual Arts'),
        ('music', 'Music'),
        ('physical_education', 'Physical Education'),
        ('health_education', 'Health Education'),
    ]
    
    GRADE_CHOICES = [
        ('A1', 'A1'),
        ('B2', 'B2'),
        ('B3', 'B3'),
        ('C4', 'C4'),
        ('C5', 'C5'),
        ('C6', 'C6'),
        ('D7', 'D7'),
        ('E8', 'E8'),
        ('F9', 'F9'),
    ]
    
    screening_form = models.ForeignKey('ScreeningForm', on_delete=models.CASCADE, related_name='academic_subjects')
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)
    grade = models.CharField(max_length=2, choices=GRADE_CHOICES)
    sitting = models.CharField(max_length=10, choices=[('first', 'First Sitting'), ('second', 'Second Sitting')])
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['screening_form', 'subject', 'sitting']
        ordering = ['subject']
    
    def __str__(self):
        return f"{self.get_subject_display()} - {self.grade} ({self.get_sitting_display()})"

class Applicant(models.Model):
    MODE_CHOICES = (
        ('open', 'Open'),
        ('utme', 'UTME'),
        ('de', 'DE'),
    )
    STATUS_CHOICES = (
        ('not_applied', 'Not Applied'),
        ('pending_review', 'Pending Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    NIGERIAN_STATES = [(state, state) for state in NIGERIA_STATES_AND_LGAS.keys()]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applicants')
    state = models.CharField(choices=NIGERIAN_STATES, max_length=100)
    phone_number = models.CharField(max_length=15)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=(('M', 'Male'), ('F', 'Female')), blank=True, null=True)
    programs = models.ForeignKey(Program, on_delete=models.SET_NULL, null=True)
    mode = models.CharField(choices=MODE_CHOICES, max_length=10)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_applied')
    
    def __str__(self):
        return self.user.username

class ScreeningForm(models.Model):
    applicant = models.ForeignKey(Applicant, on_delete=models.CASCADE, related_name='screening_forms')
    first_name = models.CharField(max_length=100, default='N/A')
    middle_name = models.CharField(max_length=100, blank=True, null=True, default='N/A')
    surname = models.CharField(max_length=100, default='N/A')
    date_of_birth = models.DateField(default='2000-01-01')
    sex = models.CharField(max_length=1, choices=[('M', 'Male'), ('F', 'Female')], default='M')
    state_of_origin = models.CharField(
        max_length=100,
        choices=[(state, state) for state in NIGERIA_STATES_AND_LGAS.keys()],
        default='N/A'
    )
    local_government = models.CharField(max_length=100, default='N/A')
    email = models.EmailField(default='not_provided@example.com')
    phone_number = models.CharField(max_length=15, default='N/A')
    contact_address = models.TextField(default='N/A')
    
    jamb_reg_no = models.CharField(max_length=20, default='N/A')
    jamb_score = models.CharField(default=0, max_length=3)
    
    # Academic Qualification Fields
    primary_school = models.CharField(max_length=200, default='N/A')
    primary_school_dates = models.CharField(max_length=100, default='N/A', help_text="Format: 2012-2018")
    secondary_school = models.CharField(max_length=200, default='N/A')
    secondary_school_dates = models.CharField(max_length=100, default='N/A', help_text="Format: 2018-2024")
    
    first_choice = models.ForeignKey(ProgramChoice, on_delete=models.SET_NULL, null=True, related_name='first_choices', default=None)
    second_choice = models.ForeignKey(ProgramChoice, on_delete=models.SET_NULL, null=True, blank=True, related_name='second_choices', default=None)
    third_choice = models.ForeignKey(ProgramChoice, on_delete=models.SET_NULL, null=True, blank=True, related_name='third_choices', default=None)
    
    waec_result = models.FileField(upload_to='waec/', default='test.docx')
    jamb_result_slip = models.FileField(upload_to='jamb/', default='test.docx')
    birth_certificate = models.FileField(upload_to='birth_certificate/', blank=True, null=True, default='test.docx')
    passport_photo = models.FileField(upload_to='passport/', default ='test.docx')

    # Document Verification Status Fields
    VERIFICATION_STATUS_CHOICES = [
        ('pending', 'Pending Verification'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
    ]

    waec_result_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='pending',
        help_text='Verification status for WAEC/NECO result'
    )
    waec_result_comment = models.TextField(
        blank=True,
        null=True,
        help_text='Comment if document is rejected'
    )

    jamb_result_slip_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='pending',
        help_text='Verification status for JAMB result slip'
    )
    jamb_result_slip_comment = models.TextField(
        blank=True,
        null=True,
        help_text='Comment if document is rejected'
    )

    passport_photo_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='pending',
        help_text='Verification status for passport photo'
    )
    passport_photo_comment = models.TextField(
        blank=True,
        null=True,
        help_text='Comment if document is rejected'
    )

    birth_certificate_status = models.CharField(
        max_length=20,
        choices=VERIFICATION_STATUS_CHOICES,
        default='pending',
        help_text='Verification status for birth certificate'
    )
    birth_certificate_comment = models.TextField(
        blank=True,
        null=True,
        help_text='Comment if document is rejected'
    )

    # Verification metadata
    verified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verified_forms',
        help_text='Admin who verified/rejected documents'
    )
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When documents were last verified/rejected'
    )

    declaration = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Screening Form for {self.applicant.user.username}"
    
    def get_first_sitting_subjects(self):
        """Get all first sitting subjects"""
        return self.academic_subjects.filter(sitting='first')
    
    def get_second_sitting_subjects(self):
        """Get all second sitting subjects"""
        return self.academic_subjects.filter(sitting='second')
    
    def get_first_sitting_examination(self):
        """Get first sitting examination details"""
        return self.examination_details.filter(sitting='first').first()
    
    def get_second_sitting_examination(self):
        """Get second sitting examination details"""
        return self.examination_details.filter(sitting='second').first()
    
    def clean(self):
        super().clean()
        # Validate LGA belongs to selected state
        if self.state_of_origin and self.local_government:
            if self.state_of_origin in NIGERIA_STATES_AND_LGAS:
                if self.local_government not in NIGERIA_STATES_AND_LGAS[self.state_of_origin]:
                    raise ValidationError({
                        'local_government': f'Invalid LGA for {self.state_of_origin} state.'
                    })

        # Validate course choices are different
        choices = [self.first_choice, self.second_choice, self.third_choice]
        choices = [c for c in choices if c is not None]
        if len(set(choices)) != len(choices):
            raise ValidationError('Course choices must be different')

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def get_document_verification_summary(self):
        """Get a summary of document verification statuses"""
        documents = {
            'WAEC/NECO Result': self.waec_result_status,
            'JAMB Result Slip': self.jamb_result_slip_status,
            'Passport Photo': self.passport_photo_status,
        }
        if self.birth_certificate:
            documents['Birth Certificate'] = self.birth_certificate_status

        verified = sum(1 for status in documents.values() if status == 'verified')
        rejected = sum(1 for status in documents.values() if status == 'rejected')
        pending = sum(1 for status in documents.values() if status == 'pending')

        return {
            'total': len(documents),
            'verified': verified,
            'rejected': rejected,
            'pending': pending,
            'all_verified': verified == len(documents),
            'has_rejected': rejected > 0,
        }

    def has_rejected_documents(self):
        """Check if any documents are rejected"""
        return any([
            self.waec_result_status == 'rejected',
            self.jamb_result_slip_status == 'rejected',
            self.passport_photo_status == 'rejected',
            self.birth_certificate_status == 'rejected' if self.birth_certificate else False,
        ])

    def all_documents_verified(self):
        """Check if all required documents are verified"""
        required_verified = all([
            self.waec_result_status == 'verified',
            self.jamb_result_slip_status == 'verified',
            self.passport_photo_status == 'verified',
        ])
        # Check birth certificate only if uploaded
        if self.birth_certificate:
            return required_verified and self.birth_certificate_status == 'verified'
        return required_verified
