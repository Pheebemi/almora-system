from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('staff-dashboard/', views.staff_dashboard, name='staff_dashboard'),
    path('courses/', views.courses, name='courses'),
    path('timetable/', views.timetable, name='timetable'),
    path('support/', views.support, name='support'),
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark-as-read/<int:notification_id>/', views.mark_notification_as_read, name='mark_notification_as_read'),
    path('support-request/<int:support_request_id>/', views.support_request_detail, name='support_request_detail'),
]