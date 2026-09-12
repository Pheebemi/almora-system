from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from .models import (
    User, Faculty, Department, StudentProfile, StaffProfile,
    Course, CourseRegistration, AcademicRecord, PaymentTransaction
)
from .serializers import (
    UserSerializer, FacultySerializer, DepartmentSerializer,
    StudentProfileSerializer, StaffProfileSerializer, CourseSerializer,
    CourseRegistrationSerializer, AcademicRecordSerializer, PaymentTransactionSerializer
)


class LoginRateThrottle(AnonRateThrottle):
    rate = '5/min'


# Authentication Views
@api_view(['POST'])
@csrf_exempt
@throttle_classes([LoginRateThrottle])
def login_view(request):
    """API login endpoint"""
    username = request.data.get('username')
    password = request.data.get('password')

    if not username or not password:
        return Response(
            {'error': 'Username and password are required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)
        serializer = UserSerializer(user)
        return Response({
            'message': 'Login successful',
            'user': serializer.data
        })
    else:
        return Response(
            {'error': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )


# User Profile Views
class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


# Faculty Views
class FacultyListView(generics.ListAPIView):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    permission_classes = [IsAuthenticated]


class FacultyDetailView(generics.RetrieveAPIView):
    queryset = Faculty.objects.all()
    serializer_class = FacultySerializer
    permission_classes = [IsAuthenticated]


# Department Views
class DepartmentListView(generics.ListAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]


class DepartmentDetailView(generics.RetrieveAPIView):
    queryset = Department.objects.all()
    serializer_class = DepartmentSerializer
    permission_classes = [IsAuthenticated]


# Student Profile Views
class StudentProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = StudentProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.studentprofile


# Staff Profile Views
class StaffProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = StaffProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.staffprofile


# Course Views
class CourseListView(generics.ListAPIView):
    queryset = Course.objects.filter(is_active=True)
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Course.objects.filter(is_active=True).prefetch_related(
            'offerings__department__faculty', 'offerings__level', 'created_by', 'academic_session'
        )
        department = self.request.query_params.get('department', None)
        level = self.request.query_params.get('level', None)
        semester = self.request.query_params.get('semester', None)

        if department:
            queryset = queryset.filter(offerings__department_id=department)
        if level:
            queryset = queryset.filter(offerings__level_id=level)
        if semester:
            queryset = queryset.filter(semester=semester)

        return queryset


class CourseDetailView(generics.RetrieveAPIView):
    queryset = Course.objects.filter(is_active=True)
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]


# Course Registration Views
class CourseRegistrationListView(generics.ListCreateAPIView):
    serializer_class = CourseRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.user_type == 'student':
            return CourseRegistration.objects.filter(student__user=self.request.user)
        elif self.request.user.user_type == 'staff':
            return CourseRegistration.objects.filter(course__department__staff_department=self.request.user.staffprofile)
        return CourseRegistration.objects.none()

    def perform_create(self, serializer):
        if self.request.user.user_type == 'student':
            serializer.save(student=self.request.user.studentprofile)


class CourseRegistrationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CourseRegistrationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.user_type == 'student':
            return CourseRegistration.objects.filter(student__user=self.request.user)
        return CourseRegistration.objects.none()


# Academic Record Views
class AcademicRecordListView(generics.ListAPIView):
    serializer_class = AcademicRecordSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.user_type == 'student':
            return AcademicRecord.objects.filter(student__user=self.request.user)
        return AcademicRecord.objects.none()


# Payment Transaction Views
class PaymentTransactionListView(generics.ListAPIView):
    serializer_class = PaymentTransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if self.request.user.user_type == 'student':
            return PaymentTransaction.objects.filter(student__user=self.request.user)
        return PaymentTransaction.objects.none()


# Dashboard Data Views
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """Get dashboard statistics for the current user"""
    user = request.user

    if user.user_type == 'student':
        try:
            profile = user.studentprofile
            stats = {
                'user_type': 'student',
                'cgpa': str(profile.cgpa),
                'current_level': profile.current_level.display_name,
                'current_semester': profile.current_semester,
                'registered_courses': CourseRegistration.objects.filter(
                    student=profile, status='registered'
                ).count(),
                'pending_payments': PaymentTransaction.objects.filter(
                    student=profile, status='pending'
                ).count()
            }
        except StudentProfile.DoesNotExist:
            stats = {'user_type': 'student', 'error': 'Profile not found'}

    elif user.user_type == 'staff':
        try:
            profile = user.staffprofile
            stats = {
                'user_type': 'staff',
                'staff_type': profile.staff_type,
                'department': profile.department.name,
                'faculty': profile.faculty.name,
                'is_head_of_department': profile.is_head_of_department
            }
        except StaffProfile.DoesNotExist:
            stats = {'user_type': 'staff', 'error': 'Profile not found'}
    else:
        stats = {'user_type': user.user_type}

    return Response(stats)