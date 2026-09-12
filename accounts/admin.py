from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import (User, StaffProfile, StudentProfile, AcademicRecord, PaymentTransaction,
    Faculty, Department, Course, CourseOffering, CourseRegistration, Enrollment,
    Verification, AcademicSession, Level, FeeStructure,
    ExamOfficerProfile, Result, SemesterGPA)

# Customizing the User Admin
@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    model = User
    # Fields to display in the user list view
    list_display = ('username', 'email', 'user_type', 'id_number', 'is_verified')
    list_filter = ('user_type', 'is_verified')
    search_fields = ('username', 'email', 'id_number')

    # Sections for editing a user
    fieldsets = (
        (None, {
            'fields': ('username', 'password', 'email', 'user_type', 'id_number', 'is_verified')
        }),
        ('Personal Info', {
            'fields': ('first_name', 'last_name', 'phone_number', 'profile_picture')
        }),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Important Dates', {
            'fields': ('last_login', 'date_joined')
        }),
    )

    # Fields for creating a new user
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'user_type', 'id_number', 'password1', 'password2')
        }),
    )

    ordering = ('username',)  # Default ordering

# Customizing StudentProfile Admin
@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'programme_type', 'faculty', 'department', 'current_level', 'current_semester', 'current_session', 'cgpa']
    search_fields = ['user__username', 'user__id_number', 'user__email']
    list_filter = ('programme_type', 'faculty', 'department', 'current_level', 'current_semester', 'current_session', 'state_of_origin')
    ordering = ('user__username',)
    list_editable = ('current_level', 'current_semester', 'current_session', 'cgpa')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name in ('faculty', 'department', 'current_level'):
            obj = getattr(request, '_student_profile_obj', None)
            if obj and hasattr(obj, 'programme_type') and obj.programme_type:
                if db_field.name == 'faculty':
                    kwargs['queryset'] = Faculty.objects.filter(programme_type=obj.programme_type).order_by('name')
                elif db_field.name == 'department':
                    kwargs['queryset'] = Department.objects.filter(faculty__programme_type=obj.programme_type).select_related('faculty').order_by('name')
                elif db_field.name == 'current_level':
                    kwargs['queryset'] = Level.objects.filter(programme_type=obj.programme_type).order_by('order')
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_form(self, request, obj=None, **kwargs):
        request._student_profile_obj = obj
        return super().get_form(request, obj, **kwargs)

# Customizing StaffProfile Admin
@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'staff_id', 'faculty', 'department', 'staff_type', 'is_head_of_department')
    list_filter = ('faculty', 'department', 'staff_type', 'is_head_of_department')
    search_fields = ('user__username', 'staff_id', 'user__email')

# Faculty Admin
@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'programme_type', 'created_at')
    list_filter = ('programme_type',)
    search_fields = ('name', 'short_name')

# Department Admin
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'short_name', 'faculty', 'created_at')
    list_filter = ('faculty',)
    search_fields = ('name', 'short_name', 'faculty__name')

# Course Admin
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'title', 'academic_session', 'semester', 'credits', 'is_active', 'created_at', 'offering_count')
    search_fields = ('code', 'title')
    list_filter = ('academic_session', 'semester', 'is_active')
    list_editable = ('is_active',)

    def offering_count(self, obj):
        return obj.offerings.count()
    offering_count.short_description = 'Departments Offering'

# Course Offering Admin
@admin.register(CourseOffering)
class CourseOfferingAdmin(admin.ModelAdmin):
    list_display = ('course', 'department', 'level', 'is_active', 'created_at')
    search_fields = ('course__code', 'course__title', 'department__name', 'level__display_name')
    list_filter = ('department', 'level', 'is_active', 'course__academic_session')
    list_editable = ('is_active',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('course', 'department', 'level')

@admin.register(CourseRegistration)
class CourseRegistrationAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'registration_date', 'status')
    search_fields = ('student__username', 'course__title')
    list_filter = ('status',)

# AcademicRecord Admin
@admin.register(AcademicRecord)
class AcademicRecordAdmin(admin.ModelAdmin):
    list_display = ('student', 'semester', 'year', 'semester_gpa')
    list_filter = ('semester', 'year')
    search_fields = ('student__user__username', 'student__user__id_number')

# Enrollment Admin
@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'semester', 'year', 'grade')
    list_filter = ('semester', 'year', 'grade')
    search_fields = ('student__user__username', 'course__course_name')

# Verification Admin
@admin.register(Verification)
class VerificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'verification_type', 'is_verified', 'verification_date', 'verified_by')
    list_filter = ('is_verified', 'verification_type')
    search_fields = ('user__username', 'verified_by__user__username')

@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ['student', 'payment_type', 'amount', 'reference', 'status', 'session']
    search_fields = ('student__user__username', 'student__user__id_number', 'session', 'semester')
    list_filter = ('status', 'session', 'semester', 'payment_type')
    list_editable = ('status',)

# Academic Session Admin
@admin.register(AcademicSession)
class AcademicSessionAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_year', 'end_year', 'session_type', 'is_active', 'start_date', 'end_date')
    list_filter = ('session_type', 'is_active', 'start_year')
    search_fields = ('name',)
    ordering = ('-start_year', '-end_year')

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('-start_year', '-end_year')

# Level Admin
@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('name', 'display_name', 'programme_type', 'order', 'is_active')
    list_filter = ('programme_type', 'is_active',)
    search_fields = ('name', 'display_name')
    ordering = ('order',)

# Fee Structure Admin
@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):
    list_display = ('academic_session', 'department', 'level', 'amount')
    list_filter = ('academic_session', 'department', 'level')
    search_fields = ('academic_session__name', 'department__name', 'level__display_name')
    ordering = ('academic_session', 'department', 'level')
    list_editable = ('amount',)


# Exam Officer Profile Admin
@admin.register(ExamOfficerProfile)
class ExamOfficerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'staff_id', 'can_manage_degree', 'can_manage_nd', 'can_manage_nce')
    list_filter = ('can_manage_degree', 'can_manage_nd', 'can_manage_nce')
    search_fields = ('user__username', 'user__email', 'staff_id')
    list_editable = ('can_manage_degree', 'can_manage_nd', 'can_manage_nce')


# Result Admin
@admin.register(Result)
class ResultAdmin(admin.ModelAdmin):
    list_display = ('student', 'course', 'test_score', 'exam_score', 'total_score', 'grade', 'grade_point', 'academic_session', 'semester', 'level', 'uploaded_by')
    list_filter = ('academic_session', 'semester', 'grade', 'level')
    search_fields = ('student__user__username', 'student__user__id_number', 'course__code', 'course__title')
    readonly_fields = ('total_score', 'grade', 'grade_point', 'uploaded_at')
    ordering = ('-uploaded_at',)


# SemesterGPA Admin
@admin.register(SemesterGPA)
class SemesterGPAAdmin(admin.ModelAdmin):
    list_display = ('student', 'academic_session', 'semester', 'level', 'gpa', 'cgpa', 'total_credits')
    list_filter = ('academic_session', 'semester', 'level')
    search_fields = ('student__user__username', 'student__user__id_number')
    ordering = ('-academic_session__start_year', 'student__user__username')
