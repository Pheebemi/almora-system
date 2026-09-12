from rest_framework import serializers
from .models import (
    User, Faculty, Department, StudentProfile, StaffProfile,
    Course, CourseOffering, CourseRegistration, AcademicRecord, PaymentTransaction
)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'first_name', 'last_name',
            'user_type', 'is_verified', 'phone_number', 'profile_picture',
            'id_number', 'date_joined'
        ]
        read_only_fields = ['date_joined']


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ['id', 'name', 'short_name', 'image', 'description', 'created_at']


class DepartmentSerializer(serializers.ModelSerializer):
    faculty = FacultySerializer(read_only=True)

    class Meta:
        model = Department
        fields = ['id', 'name', 'faculty', 'short_name', 'created_at']


class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    faculty = FacultySerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = StudentProfile
        fields = [
            'id', 'user', 'date_of_birth', 'gender', 'faculty', 'department',
            'program', 'admission_year', 'current_level', 'current_semester',
            'permanent_address', 'state_of_origin', 'local_government', 'cgpa'
        ]


class StaffProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    faculty = FacultySerializer(read_only=True)
    department = DepartmentSerializer(read_only=True)

    class Meta:
        model = StaffProfile
        fields = [
            'id', 'user', 'staff_id', 'staff_type', 'faculty', 'department',
            'qualification', 'date_employed', 'is_head_of_department'
        ]


class CourseOfferingSerializer(serializers.ModelSerializer):
    department = DepartmentSerializer(read_only=True)
    level = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = CourseOffering
        fields = ['department', 'level']


class CourseCreatorSerializer(serializers.ModelSerializer):
    """Minimal staff info exposed on courses — no PII."""
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name']


class CourseSerializer(serializers.ModelSerializer):
    offerings = CourseOfferingSerializer(many=True, read_only=True)
    created_by = CourseCreatorSerializer(read_only=True)
    academic_session = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Course
        fields = [
            'id', 'code', 'title', 'description', 'credits', 'offerings',
            'semester', 'academic_session', 'created_by', 'created_at', 'updated_at', 'is_active'
        ]


class CourseRegistrationSerializer(serializers.ModelSerializer):
    student = StudentProfileSerializer(read_only=True)
    course = CourseSerializer(read_only=True)

    class Meta:
        model = CourseRegistration
        fields = ['id', 'student', 'course', 'registration_date', 'status']


class AcademicRecordSerializer(serializers.ModelSerializer):
    student = StudentProfileSerializer(read_only=True)
    courses = CourseSerializer(many=True, read_only=True)

    class Meta:
        model = AcademicRecord
        fields = ['id', 'student', 'semester', 'year', 'courses', 'semester_gpa']


class PaymentTransactionSerializer(serializers.ModelSerializer):
    student = StudentProfileSerializer(read_only=True)

    class Meta:
        model = PaymentTransaction
        fields = [
            'id', 'student', 'payment_type', 'amount', 'reference',
            'paystack_reference', 'status', 'session', 'semester',
            'payment_date', 'verified_at'
        ]