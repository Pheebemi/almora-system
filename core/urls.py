from django.urls import path
from . import views
from django.conf import settings



app_name = 'core'

urlpatterns = [
    path('health/', views.health_check, name='health_check'),
    path('', views.landing_page, name='landing_page'),
    path('apply/', views.create_applicant, name='apply_page'),
    path('contact/', views.contact_page, name='contact_page'),
    path('about/', views.about_page, name='about_page'),
    path('programs/', views.programs_list, name='programs_page'),  # Add this line
    path('programs/<str:pk>', views.program_detail, name='program'),
    path('applicant/', views.applicant_login, name='applicant_login'),
    path('applicant/dashboard/', views.applicant_dashboard, name='applicant_dashboard'),
    path('applicant/screening/payment/', views.screening_payment_wall, name='screening_payment_wall'),
    path('applicant/screening/payment/initiate/', views.initiate_screening_payment, name='initiate_screening_payment'),
    path('applicant/screening/payment/verify/<str:reference>/', views.verify_screening_payment, name='verify_screening_payment'),
    path('applicant/screening/', views.screening_form, name='screening_form'),
    path('applicant/payment/receipt/', views.applicant_payment_receipt, name='applicant_payment_receipt'),
    path('screening-form/data/', views.get_screening_form_data, name='get_screening_form_data'),
    path('api/program-choices/<str:program_type>/', views.get_program_choices, name='get_program_choices'),
    path('student-profile/data/', views.get_student_profile_data, name='get_student_profile_data'),
    path('student-courses/data/', views.get_student_course_data, name='get_student_course_data'),
    path('generate-pdf/<int:user_id>/', views.generate_pdf, name='generate_pdf'),  # Add this line
]
