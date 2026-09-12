from django.urls import path
from . import api_views

app_name = 'accounts_api'

urlpatterns = [
    # Authentication
    path('login/', api_views.login_view, name='api_login'),

    # User Profile
    path('profile/', api_views.UserProfileView.as_view(), name='user_profile'),

    # Faculty
    path('faculties/', api_views.FacultyListView.as_view(), name='faculty_list'),
    path('faculties/<int:pk>/', api_views.FacultyDetailView.as_view(), name='faculty_detail'),

    # Department
    path('departments/', api_views.DepartmentListView.as_view(), name='department_list'),
    path('departments/<int:pk>/', api_views.DepartmentDetailView.as_view(), name='department_detail'),

    # Student Profile
    path('student-profile/', api_views.StudentProfileView.as_view(), name='student_profile'),

    # Staff Profile
    path('staff-profile/', api_views.StaffProfileView.as_view(), name='staff_profile'),

    # Courses
    path('courses/', api_views.CourseListView.as_view(), name='course_list'),
    path('courses/<int:pk>/', api_views.CourseDetailView.as_view(), name='course_detail'),

    # Course Registration
    path('course-registrations/', api_views.CourseRegistrationListView.as_view(), name='course_registration_list'),
    path('course-registrations/<int:pk>/', api_views.CourseRegistrationDetailView.as_view(), name='course_registration_detail'),

    # Academic Records
    path('academic-records/', api_views.AcademicRecordListView.as_view(), name='academic_record_list'),

    # Payment Transactions
    path('payment-transactions/', api_views.PaymentTransactionListView.as_view(), name='payment_transaction_list'),

    # Dashboard Stats
    path('dashboard-stats/', api_views.dashboard_stats, name='dashboard_stats'),
]