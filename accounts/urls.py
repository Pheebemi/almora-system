from django.urls import path
from . import views, course_views, app_manager_views, exam_officer_views


app_name = 'accounts'

urlpatterns = [
    path('logout/', views.logout_user, name='logout'),
    path('student-profile/', views.student_profile, name='student_profile'),
    path('staff-profile/', views.staff_profile, name='staff_profile'),
    path('edit-student-profile/', views.edit_student_profile, name='edit_student_profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('edit-staff-profile/', views.edit_staff_profile, name='edit_staff_profile'),
    path('create-course/', course_views.create_course, name='create_course'),
    path('manage-courses/', course_views.manage_courses, name='manage_courses'),
    path('register-courses/', course_views.register_courses, name='register_courses'),
    path('registered-courses/', course_views.view_registered_courses, name='view_registered_courses'),
    path('student/courses/', views.student_courses, name='student_courses'),  # Ensure this line is present
    path('department-students/', views.department_students, name='department_students'),
    path('create-student/', views.create_student, name='create_student'),
    path('student/<int:student_id>/', views.student_detail, name='student_detail'),
    path('school-fees/', views.school_fees, name='school_fees'),
    path('initiate-payment/', views.initiate_payment, name='initiate_payment'),
    path('verify-payment/<path:reference>/', views.verify_payment, name='verify_payment'),
    path('payment-receipt/<int:payment_id>/', views.payment_receipt, name='payment_receipt'),
    #path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('student-attendance/', views.student_attendance, name='student_attendance'),
    # path('login/', views, name='login'),

    # Application Manager URLs
    path('app-manager/dashboard/', app_manager_views.app_manager_dashboard, name='app_manager_dashboard'),
    path('app-manager/applicants/', app_manager_views.applicants_list, name='app_manager_applicants_list'),
    path('app-manager/applicants/<int:applicant_id>/', app_manager_views.applicant_detail, name='app_manager_applicant_detail'),
    path('app-manager/documents/', app_manager_views.app_manager_documents, name='app_manager_documents'),
    path('app-manager/merit-list/', app_manager_views.app_manager_merit_list, name='app_manager_merit_list'),
    path('app-manager/communicate/', app_manager_views.app_manager_communicate, name='app_manager_communicate'),

    # Exam Officer URLs
    path('exam-officer/dashboard/', exam_officer_views.exam_officer_dashboard, name='exam_officer_dashboard'),
    path('exam-officer/select-course/', exam_officer_views.select_course, name='exam_officer_select_course'),
    path('exam-officer/upload-results/<int:course_id>/', exam_officer_views.upload_results, name='exam_officer_upload_results'),
    path('exam-officer/student-gpas/', exam_officer_views.view_student_gpas, name='exam_officer_student_gpas'),
    path('exam-officer/results-sheet/', exam_officer_views.department_results_sheet, name='exam_officer_results_sheet'),
]