from django.contrib.auth.models import AbstractUser
from django.db import models
from .state import NIGERIA_STATES_AND_LGAS
from django.core.exceptions import ValidationError


class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('student', 'Student'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
        ('exam_officer', 'Exam Officer'),
        ('applicant', 'Applicant'),
        ('application_manager', 'Application Manager')
    )

    user_type = models.CharField(max_length=25, choices=USER_TYPE_CHOICES)
    is_verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    id_number = models.CharField(
        max_length=30,
        unique=True,
        blank=True,
        null=True,
        help_text="Student ID number (e.g., LCE/DIP/CMP/24/0001) or Staff ID. Manually assigned."
    )
    

    def clean(self):
        """
        Custom validation to ensure id_number is only set for students or staff.
        """
        if self.user_type not in ['student', 'staff'] and self.id_number:
            raise ValidationError("ID number can only be set for students or staff.")

    def save(self, *args, **kwargs):
        self.clean()  # Call the clean method for validation
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.user_type})"
    
    
PROGRAMME_TYPE_CHOICES = (
    ('degree', 'Degree'),
    ('nd', 'ND (Diploma)'),
    ('nce', 'NCE'),
)


class Faculty(models.Model):
    name = models.CharField(max_length=100)
    short_name = models.CharField(max_length=30)
    programme_type = models.CharField(
        max_length=10,
        choices=PROGRAMME_TYPE_CHOICES,
        default='degree',
        help_text='Degree, ND (Diploma), or NCE'
    )
    image = models.ImageField(upload_to='faculty/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def faculty_img(self):
        if self.image:
            return self.image.url
        else:
            return 'https://fakeimg.pl/600x400'
    
    class Meta:
        verbose_name_plural = 'Faculties'


class AcademicSession(models.Model):
    SESSION_TYPE_CHOICES = (
        ('regular', 'Regular Session'),
        ('special', 'Special Session'),
    )

    name = models.CharField(max_length=20, unique=True, help_text="e.g., '2023/2024'")
    start_year = models.PositiveIntegerField(help_text="Starting year, e.g., 2023")
    end_year = models.PositiveIntegerField(help_text="Ending year, e.g., 2024")
    session_type = models.CharField(max_length=10, choices=SESSION_TYPE_CHOICES, default='regular')
    is_active = models.BooleanField(default=False, help_text="Only one session can be active at a time")
    start_date = models.DateField(help_text="Session start date")
    end_date = models.DateField(help_text="Session end date")
    registration_deadline = models.DateField(help_text="Last date for course registration")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_year', '-end_year']
        verbose_name = 'Academic Session'
        verbose_name_plural = 'Academic Sessions'

    def __str__(self):
        return f"{self.name} ({self.session_type})"

    def save(self, *args, **kwargs):
        # Ensure only one active session at a time
        if self.is_active:
            AcademicSession.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)

    @property
    def is_current(self):
        """Check if this session is currently active"""
        from django.utils import timezone
        today = timezone.now().date()
        return self.start_date <= today <= self.end_date

class Level(models.Model):
    name = models.CharField(max_length=10, unique=True, help_text="e.g., '100', '200', 'ND1', 'NCE1'")
    display_name = models.CharField(max_length=20, help_text="e.g., '100 Level', 'ND 1', 'NCE 1'")
    order = models.PositiveIntegerField(unique=True, help_text="Order for progression (1 for 100, 2 for 200, etc.)")
    programme_type = models.CharField(
        max_length=10,
        choices=PROGRAMME_TYPE_CHOICES,
        default='degree',
        help_text='Degree (100-400), ND (ND1-ND2), or NCE (NCE1-NCE2)'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Academic Level'
        verbose_name_plural = 'Academic Levels'

    def __str__(self):
        return self.display_name


class Attendance(models.Model):
    student = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'student'})
    date = models.DateField()
    status = models.CharField(max_length=10, choices=[('present', 'Present'), ('absent', 'Absent')])

    def __str__(self):
        return f"{self.student.get_full_name()} - {self.date} - {self.status}"

class Department(models.Model):
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='departments')
    short_name = models.CharField(max_length=30)
    name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


# Fee Structure Model
class FeeStructure(models.Model):
    academic_session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name='fee_structures')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='fee_structures')
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='fee_structures')
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Fee amount in Naira")

    class Meta:
        unique_together = ('academic_session', 'department', 'level')
        ordering = ['academic_session', 'department', 'level']
        verbose_name = 'Fee Structure'
        verbose_name_plural = 'Fee Structures'

    def __str__(self):
        return f"{self.academic_session.name} - {self.department.name} - {self.level.display_name} - ₦{self.amount}"

class StudentProfile(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other')
    )
    PROGRAM_CHOICES = (
        ('BSc', 'Bachelor of Science'),
        ('BA', 'Bachelor of Arts'),
        ('BEng', 'Bachelor of Engineering'),
        ('LLB', 'Bachelor of Laws'),
        ('MBBS', 'Bachelor of Medicine, Bachelor of Surgery'),
        ('PharmD', 'Doctor of Pharmacy'),
        ('BBA', 'Bachelor of Business Administration'),
        ('BCom', 'Bachelor of Commerce'),
        ('BEd', 'Bachelor of Education'),
        ('BFA', 'Bachelor of Fine Arts'),
        ('BPharm', 'Bachelor of Pharmacy'),
        ('BTech', 'Bachelor of Technology'),
        ('BVSc', 'Bachelor of Veterinary Science'),
    )
    SEMESTER_CHOICES = (
        ('first', 'First Semester'),
        ('second', 'Second Semester'),
    )
    NIGERIAN_STATES = [(state, state) for state in NIGERIA_STATES_AND_LGAS.keys()]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='studentprofile')
    programme_type = models.CharField(
        max_length=10,
        choices=PROGRAMME_TYPE_CHOICES,
        default='degree',
        help_text='Degree, ND (Diploma), or NCE - determines which faculties/levels apply'
    )
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='user_faculty', default=1)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='user_department', default=1)
    program = models.CharField(max_length=10, choices=PROGRAM_CHOICES)
    admission_year = models.CharField(max_length=10, choices=[(str(year), str(year)) for year in range(1900, 2101)])
    current_level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='students')
    current_semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES, default='first')
    current_session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name='students', null=True, blank=True)
    permanent_address = models.CharField(max_length=100, blank=True, null=True)
    state_of_origin = models.CharField(max_length=100, choices=NIGERIAN_STATES, verbose_name="State of Origin")
    local_government = models.CharField(max_length=100, verbose_name="Local Government")
    cgpa = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)

    @property
    def is_profile_complete(self):
        """Check if all required profile fields are filled"""
        required_fields = [
            self.user.first_name,
            self.user.last_name,
            self.user.email,
            self.user.phone_number,
            self.user.profile_picture,
            self.date_of_birth,
            self.gender,
            self.state_of_origin,
            self.local_government,
            self.permanent_address
        ]
        return all(field for field in required_fields)

    def __str__(self):
        return f"{self.user.username} - {self.user.id_number}"

class AcademicRecord(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    semester = models.CharField(max_length=10, choices=(
        ('first', 'first'),
        ('second', 'second')
    ))
    year = models.CharField(max_length=10, choices=[(str(year), str(year)) for year in range(1900, 2101)])
    courses = models.ManyToManyField("Course", related_name='academic_courses')  
    semester_gpa = models.DecimalField(max_digits=3, decimal_places=2)
    
    def __str__(self):
        return f"{self.student.user.username} - Semester {self.semester} {self.year}"
    
    
    
class StaffProfile(models.Model):
    STAFF_TYPE_CHOICES = (
        ('academic', 'Academic Staff'),
        ('non_academic', 'Non-Academic Staff')
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    staff_id = models.CharField(max_length=20, unique=True)
    staff_type = models.CharField(max_length=20, choices=STAFF_TYPE_CHOICES)
    
    # For Academic Staff
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name='staff_faculty')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='staff_department')
    qualification = models.CharField(max_length=100)
    
    # Additional Staff Details
    date_employed = models.DateField(blank=True, null=True)
    is_head_of_department = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.user.username} - {self.staff_id}"



# Course Model
class Course(models.Model):
    SEMESTER_CHOICES = (
        ('first', 'First Semester'),
        ('second', 'Second Semester'),
    )

    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    credits = models.IntegerField()
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES)
    academic_session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name='courses', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['code']

    def __str__(self):
        return f"{self.code} - {self.title}"

    def get_offering_departments(self):
        """Get all departments that offer this course"""
        return [offering.department for offering in self.offerings.all()]

    def get_offering_levels(self):
        """Get all levels at which this course is offered"""
        return [offering.level for offering in self.offerings.all()]

# Course Offering Model - Links courses to departments and levels
class CourseOffering(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='offerings')
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='course_offerings')
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='course_offerings')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['course', 'department', 'level']
        verbose_name = 'Course Offering'
        verbose_name_plural = 'Course Offerings'
        ordering = ['course__code', 'department__name', 'level__order']

    def __str__(self):
        return f"{self.course.code} - {self.department.name} - {self.level.display_name}"

# Course Registration Model
class CourseRegistration(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='registrations')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='registrations')
    academic_session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name='registrations', null=True, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('registered', 'Registered'),
            ('dropped', 'Dropped'),
            ('completed', 'Completed')
        ],
        default='registered'
    )

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.course.title}"

    class Meta:
        unique_together = ('student', 'course', 'academic_session')  # Prevent duplicate registrations in same session

class Enrollment(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.CharField(max_length=10, choices=(
        ('first', 'first'),
        ('second', 'second')
    ))
    year = models.CharField(max_length=10, choices=[(str(year), str(year)) for year in range(1900, 2101)])
    grade = models.CharField(max_length=2, blank=True, null=True)
    
    class Meta:
        unique_together = ('student', 'course', 'semester', 'year')

class Verification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    verification_type = models.CharField(max_length=20)
    is_verified = models.BooleanField(default=False)
    verified_by = models.ForeignKey(StaffProfile, on_delete=models.SET_NULL, null=True)
    verification_date = models.DateTimeField(null=True, blank=True)
    verification_document = models.FileField(upload_to='verification_docs/', null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.username} - Verification Status"

class PaymentTransaction(models.Model):
    PAYMENT_TYPES = (
        ('school_fees', 'School Fees'),
        ('acceptance_fees', 'Acceptance Fees'),
        ('other', 'Other Fees'),
    )
    
    PAYMENT_STATUS = (
        ('pending', 'Pending'),
        ('success', 'Success'),
        ('failed', 'Failed'),
    )
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    reference = models.CharField(max_length=100, unique=True)
    paystack_reference = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=10, choices=PAYMENT_STATUS, default='pending')
    session = models.CharField(max_length=10)  # e.g., "2023/2024"
    semester = models.CharField(max_length=10, choices=StudentProfile.SEMESTER_CHOICES)
    payment_date = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.payment_type} - {self.session}"

    class Meta:
        ordering = ['-payment_date']


class ApplicationActivity(models.Model):
    """Track all actions performed on applicant records by application managers"""
    ACTION_CHOICES = (
        ('status_changed', 'Status Changed'),
        ('document_verified', 'Document Verified'),
        ('document_rejected', 'Document Rejected'),
        ('note_added', 'Note Added'),
        ('notification_sent', 'Notification Sent'),
        ('admission_offered', 'Admission Offered'),
        ('admission_rejected', 'Admission Rejected'),
    )

    applicant = models.ForeignKey('core.Applicant', on_delete=models.CASCADE, related_name='activities')
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='managed_activities')
    action = models.CharField(max_length=30, choices=ACTION_CHOICES)
    details = models.TextField(help_text="Description of the action taken")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']
        verbose_name_plural = 'Application Activities'

    def __str__(self):
        return f"{self.action} - {self.applicant.user.get_full_name()} by {self.manager.get_full_name() if self.manager else 'System'}"


class ApplicationNote(models.Model):
    """Internal notes/comments on applicant records by application managers"""
    applicant = models.ForeignKey('core.Applicant', on_delete=models.CASCADE, related_name='notes')
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='application_notes')
    note = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Note by {self.manager.get_full_name() if self.manager else 'Unknown'} on {self.applicant.user.get_full_name()}"


class ExamOfficerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='examofficerprofile')
    staff_id = models.CharField(max_length=20, unique=True)
    # Programme types this exam officer can manage
    can_manage_degree = models.BooleanField(default=False, help_text='Can upload results for Degree programmes')
    can_manage_nd = models.BooleanField(default=False, help_text='Can upload results for ND (Diploma) programmes')
    can_manage_nce = models.BooleanField(default=False, help_text='Can upload results for NCE programmes')
    date_assigned = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Exam Officer Profile'
        verbose_name_plural = 'Exam Officer Profiles'

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.staff_id}"

    @property
    def assigned_programme_types(self):
        """Return a list of programme types this officer can manage"""
        types = []
        if self.can_manage_degree:
            types.append('degree')
        if self.can_manage_nd:
            types.append('nd')
        if self.can_manage_nce:
            types.append('nce')
        return types


GRADE_SCALE = (
    ('A', 'A (70-100)'),
    ('B', 'B (60-69)'),
    ('C', 'C (50-59)'),
    ('D', 'D (45-49)'),
    ('E', 'E (40-44)'),
    ('F', 'F (0-39)'),
)


class Result(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='results')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='results')
    academic_session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name='results')
    semester = models.CharField(max_length=10, choices=(('first', 'First Semester'), ('second', 'Second Semester')))
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='results',
                              help_text='Level at the time of this result (frozen, does not change after promotion)')
    # Scores: Test = 40 marks, Exam = 60 marks
    test_score = models.DecimalField(max_digits=4, decimal_places=1, help_text='Test score out of 40')
    exam_score = models.DecimalField(max_digits=4, decimal_places=1, help_text='Exam score out of 60')
    total_score = models.DecimalField(max_digits=5, decimal_places=1, editable=False, help_text='Auto-calculated: test + exam')
    grade = models.CharField(max_length=5, choices=GRADE_SCALE, editable=False)
    grade_point = models.DecimalField(max_digits=2, decimal_places=1, editable=False)
    # Audit trail
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='uploaded_results')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'course', 'academic_session')
        ordering = ['academic_session', 'level__order', 'semester', 'course__code']
        verbose_name = 'Student Result'
        verbose_name_plural = 'Student Results'

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.course.code} - {self.grade} ({self.total_score})"

    @staticmethod
    def calculate_grade(total_score, programme_type='degree'):
        """Calculate grade and grade point from total score based on programme type"""
        score = float(total_score)
        
        if programme_type == 'nd':
            # ND (Diploma) 4.0 Scale
            if score >= 75:
                return 'A', 4.0
            elif score >= 70:
                return 'AB', 3.5
            elif score >= 65:
                return 'B', 3.25
            elif score >= 60:
                return 'BC', 3.0
            elif score >= 55:
                return 'C', 2.75
            elif score >= 50:
                return 'CD', 2.5
            elif score >= 45:
                return 'D', 2.25
            elif score >= 40:
                return 'E', 2.0
            else:
                return 'F', 0.0
        else:
            # NCE & Degree 5.0 Scale
            if score >= 70:
                return 'A', 5.0
            elif score >= 60:
                return 'B', 4.0
            elif score >= 50:
                return 'C', 3.0
            elif score >= 45:
                return 'D', 2.0
            elif score >= 40:
                return 'E', 1.0
            else:
                return 'F', 0.0

    def clean(self):
        programme_type = self.student.programme_type
        if programme_type == 'nd':
            max_test, max_exam = 40, 60
        else:
            max_test, max_exam = 30, 70

        if self.test_score is not None and (self.test_score < 0 or self.test_score > max_test):
            raise ValidationError(f'Test score for {programme_type.upper()} must be between 0 and {max_test}.')
        if self.exam_score is not None and (self.exam_score < 0 or self.exam_score > max_exam):
            raise ValidationError(f'Exam score for {programme_type.upper()} must be between 0 and {max_exam}.')

    def save(self, *args, **kwargs):
        self.clean()
        # Auto-calculate total, grade, and grade point
        self.total_score = (self.test_score or 0) + (self.exam_score or 0)
        self.grade, self.grade_point = self.calculate_grade(float(self.total_score), self.student.programme_type)
        super().save(*args, **kwargs)


class SemesterGPA(models.Model):
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='semester_gpas')
    academic_session = models.ForeignKey(AcademicSession, on_delete=models.CASCADE, related_name='semester_gpas')
    semester = models.CharField(max_length=10, choices=(('first', 'First Semester'), ('second', 'Second Semester')))
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='semester_gpas',
                              help_text='Level at the time (frozen)')
    gpa = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_credits = models.PositiveIntegerField(default=0)
    total_quality_points = models.DecimalField(max_digits=6, decimal_places=2, default=0.00,
                                                help_text='Sum of (grade_point x credits) for all courses')
    cgpa = models.DecimalField(max_digits=3, decimal_places=2, default=0.00,
                               help_text='Cumulative GPA up to and including this semester')
    is_finalized = models.BooleanField(default=False, help_text='Set to True when all results are confirmed')
    finalized_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('student', 'academic_session', 'semester')
        ordering = ['academic_session', 'semester']
        verbose_name = 'Semester GPA'
        verbose_name_plural = 'Semester GPAs'

    def __str__(self):
        return f"{self.student.user.get_full_name()} - {self.academic_session.name} {self.semester} - GPA: {self.gpa}"

    def calculate_gpa(self):
        """Calculate GPA from all results for this student/session/semester"""
        results = Result.objects.filter(
            student=self.student,
            academic_session=self.academic_session,
            semester=self.semester
        ).select_related('course')

        total_credits = 0
        total_quality_points = 0
        for result in results:
            credits = result.course.credits
            total_credits += credits
            total_quality_points += float(result.grade_point) * credits

        self.total_credits = total_credits
        self.total_quality_points = total_quality_points
        self.gpa = round(total_quality_points / total_credits, 2) if total_credits > 0 else 0.00

    def calculate_cgpa(self):
        """Calculate cumulative GPA from all semesters up to and including this one"""
        all_gpas = SemesterGPA.objects.filter(
            student=self.student,
        ).exclude(pk=self.pk)

        total_credits = self.total_credits
        total_quality_points = float(self.total_quality_points)

        for gpa_record in all_gpas:
            total_credits += gpa_record.total_credits
            total_quality_points += float(gpa_record.total_quality_points)

        self.cgpa = round(total_quality_points / total_credits, 2) if total_credits > 0 else 0.00

    def get_classification(self):
        """Return class classification based on CGPA and programme type"""
        cgpa = float(self.cgpa)
        p_type = self.student.programme_type
        
        if p_type == 'nd':
            if cgpa >= 3.50: return "Distinction"
            if cgpa >= 3.00: return "Upper Credit"
            if cgpa >= 2.50: return "Lower Credit"
            if cgpa >= 2.00: return "Pass"
            return "Fail"
        else:
            # Degree/NCE 5.0 scale (standard)
            if cgpa >= 4.50: return "First Class"
            if cgpa >= 3.50: return "Second Class (Upper)"
            if cgpa >= 2.40: return "Second Class (Lower)"
            if cgpa >= 1.50: return "Third Class"
            if cgpa >= 1.00: return "Pass"
            return "Fail"
