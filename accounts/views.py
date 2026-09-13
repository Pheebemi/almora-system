from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.db.models import Q
from .models import User, StaffProfile, StudentProfile, Course, CourseOffering, CourseRegistration, Department, PaymentTransaction, AcademicSession, Level
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from .state import NIGERIA_STATES_AND_LGAS
from django_ratelimit.decorators import ratelimit
import json
import requests
from django.conf import settings
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from .models import Attendance, CourseRegistration, StudentProfile
from .utils import resolve_login_username

# Create your views here.

#Login student or if staff to dashboard


@ratelimit(key='ip', rate='5/m', method='POST', block=False)
@csrf_exempt
def student_login(request):
    """
    Handles login for students only.
    """
    if request.method == 'POST':
        if getattr(request, 'limited', False):
            messages.error(request, "Too many login attempts. Please wait a minute and try again.")
            return render(request, 'accounts/student_login.html', status=429)

        # Check if this is a JSON request from API
        if request.content_type == 'application/x-www-form-urlencoded':
            # Get credentials from form data (API request)
            id_number = request.POST.get('username')
            password = request.POST.get('password')
        else:
            # Regular form request
            id_number = request.POST.get('username')
            password = request.POST.get('password')

        # Authenticate the user
        user = authenticate(request, username=id_number, password=password)

        if user is not None:
            if user.is_verified:  # Ensure the student is verified
                if user.user_type == 'student':  # Check if the user is a student
                    login(request, user)
                    # Check if this is an API request
                    if request.content_type == 'application/x-www-form-urlencoded':
                        # API request - redirect to dashboard
                        return redirect(reverse('dashboard:student_dashboard'))
                    else:
                        # Regular form request
                        messages.success(request, f"Student Login as '{request.user.username}' 🙌")
                        return redirect(reverse('dashboard:student_dashboard'))
                else:
                    if request.content_type == 'application/x-www-form-urlencoded':
                        # Return JSON error for API
                        return JsonResponse({'error': 'Only students are allowed to log in here.'}, status=400)
                    else:
                        messages.error(request, "Only students are allowed to log in here.")
            else:
                if request.content_type == 'application/x-www-form-urlencoded':
                    return JsonResponse({'error': 'Your account is not verified. Contact the admin.'}, status=400)
                else:
                    messages.error(request, "Your account is not verified. Contact the admin.")
        else:
            if request.content_type == 'application/x-www-form-urlencoded':
                return JsonResponse({'error': 'Invalid ID number or password.'}, status=400)
            else:
                messages.error(request, "Invalid ID number or password.")

    return render(request, 'accounts/student_login.html')


@ratelimit(key='ip', rate='5/m', method='POST', block=False)
@csrf_exempt
def staff_login(request):
    if request.method == 'POST':
        if getattr(request, 'limited', False):
            messages.error(request, "Too many login attempts. Please wait a minute and try again.")
            return render(request, 'accounts/staff_login.html', status=429)

        # Check if this is a JSON request from API
        if request.content_type == 'application/x-www-form-urlencoded':
            # Get credentials from form data (API request)
            username = request.POST.get('username')
            password = request.POST.get('password')
        else:
            # Regular form request
            username = request.POST.get('username')
            password = request.POST.get('password')

        user = authenticate(request, username=resolve_login_username(username), password=password)
        if user is not None:
            if user.is_verified:
                if user.user_type in ('staff', 'admin'):
                    login(request, user)
                    dashboard_url = 'dashboard:admin_dashboard' if user.user_type == 'admin' else 'dashboard:staff_dashboard'
                    # Check if this is an API request
                    if request.content_type == 'application/x-www-form-urlencoded':
                        # API request - redirect to dashboard
                        return redirect(reverse(dashboard_url))
                    else:
                        # Regular form request
                        messages.info(request, f'Staff Login as {request.user.username}')
                        return redirect(reverse(dashboard_url))
                else:
                    if request.content_type == 'application/x-www-form-urlencoded':
                        # Return JSON error for API
                        return JsonResponse({'error': 'Only staff members are allowed to log in here.'}, status=400)
                    else:
                        messages.error(request, "Only staffs are allowed to log in here.")
                        return redirect('staff_login')
            else:
                if request.content_type == 'application/x-www-form-urlencoded':
                    return JsonResponse({'error': 'Your account is not verified. Contact the admin.'}, status=400)
                else:
                    messages.warning(request, 'Your account is not verified. Contact the admin.')
                    return redirect('staff_login')
        else:
            if request.content_type == 'application/x-www-form-urlencoded':
                return JsonResponse({'error': 'Invalid username or password.'}, status=400)
            else:
                messages.warning(request, 'Something went wrong')
                return redirect('staff_login')
    else:
        return render(request, 'accounts/staff_login.html')



def logout_user(request):
    user_type = request.user.user_type if request.user.is_authenticated else 'student'
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    if user_type in ('staff', 'admin'):
        return redirect('staff_login')
    elif user_type == 'applicant':
        return redirect('core:applicant_login')
    elif user_type == 'application_manager':
        return redirect('app_manager_login')
    elif user_type == 'exam_officer':
        return redirect('exam_officer_login')
    else:
        return redirect('student_login')

@login_required
def student_profile(request):
    """
    Display and handle updates to student profile
    """
    try:
        profile = StudentProfile.objects.get(user=request.user)
        context = {
            'profile': profile,
            'user': request.user,
            'states': NIGERIA_STATES_AND_LGAS.keys()
        }
        return render(request, 'accounts/student_profile.html', context)
    except StudentProfile.DoesNotExist:
        messages.error(request, "Profile not found")
        return redirect('dashboard:student_dashboard')

@login_required
def edit_student_profile(request):
    """
    Handle student profile updates
    """
    profile = get_object_or_404(StudentProfile, user=request.user)
    
    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        phone_number = request.POST.get('phone_number')
        date_of_birth = request.POST.get('date_of_birth')
        gender = request.POST.get('gender')
        state_of_origin = request.POST.get('state_of_origin')
        local_government = request.POST.get('local_government')
        permanent_address = request.POST.get('permanent_address')

        profile_picture = request.FILES.get('profile_picture')

        # Validate required fields
        if not all([first_name, last_name, email, phone_number, date_of_birth, gender, state_of_origin, local_government, permanent_address]):
            messages.error(request, 'All fields are required. Please fill in all information.')
            return redirect('accounts:edit_student_profile')

        # Validate profile picture (mandatory)
        user = request.user
        if not user.profile_picture and not profile_picture:
            messages.error(request, 'Profile picture is required.')
            return redirect('accounts:edit_student_profile')

        # Validate profile picture size (max 1MB)
        if profile_picture:
            if profile_picture.size > 1 * 1024 * 1024:  # 1MB in bytes
                messages.error(request, 'Profile picture size must be 1MB or less.')
                return redirect('accounts:edit_student_profile')
            user.profile_picture = profile_picture
        
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        user.phone_number = phone_number
        
        user.save()
        
        # Update profile fields
        profile.date_of_birth = date_of_birth
        profile.gender = gender
        profile.state_of_origin = state_of_origin
        profile.local_government = local_government
        profile.permanent_address = permanent_address
        
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:student_profile')
    
    context = {
        'profile': profile,
        'user': request.user,
        'states': list(NIGERIA_STATES_AND_LGAS.keys()),
        'states_lgas': json.dumps(NIGERIA_STATES_AND_LGAS)
    }
    return render(request, 'accounts/edit_student_profile.html', context)

@login_required
def change_password(request):
    """
    Handle password changes for students
    """
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        # 1. Basic matching check
        if new_password != confirm_password:
            messages.error(request, 'New passwords do not match.')
            return redirect('accounts:change_password')

        user = request.user

        # 2. Verify old password
        if not user.check_password(old_password):
            messages.error(request, 'Incorrect old password.')
            return redirect('accounts:change_password')

        # 3. Apply Django password validation
        try:
            password_validation.validate_password(new_password, user)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return redirect('accounts:change_password')

        # 4. Save new password
        user.set_password(new_password)
        user.save()
        
        # 5. Keep user logged in
        update_session_auth_hash(request, user)
        
        messages.success(request, 'Your password has been changed successfully!')
        return redirect('dashboard:student_dashboard')

    return render(request, 'accounts/change_password.html')

@login_required
def staff_profile(request):
    """
    Display staff profile
    """
    try:
        profile = StaffProfile.objects.get(user=request.user)
        context = {
            'profile': profile,
            'user': request.user,
            'states': NIGERIA_STATES_AND_LGAS.keys()
        }
        return render(request, 'accounts/staff_profile.html', context)
    except StaffProfile.DoesNotExist:
        messages.error(request, "Profile not found")
        return redirect('dashboard:staff_dashboard')

@login_required
def edit_staff_profile(request):
    """
    Handle staff profile updates
    """
    profile = get_object_or_404(StaffProfile, user=request.user)
    
    if request.method == 'POST':
        # Get form data
        user = request.user
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')
        user.phone_number = request.POST.get('phone_number')
        
        # Handle profile picture upload
        if request.FILES.get('profile_picture'):
            user.profile_picture = request.FILES['profile_picture']
        
        user.save()
        
        # Update profile fields
        profile.date_of_birth = request.POST.get('date_of_birth')
        profile.gender = request.POST.get('gender')
        profile.state_of_origin = request.POST.get('state_of_origin')
        profile.local_government = request.POST.get('local_government')
        profile.permanent_address = request.POST.get('permanent_address')
        profile.qualification = request.POST.get('qualification')
        profile.specialization = request.POST.get('specialization')
        
        profile.save()
        
        messages.success(request, 'Profile updated successfully!')
        return redirect('accounts:staff_profile')
    
    context = {
        'profile': profile,
        'user': request.user,
        'states': NIGERIA_STATES_AND_LGAS.keys()
    }
    return render(request, 'accounts/edit_staff_profile.html', context)

def is_staff(user):
    return user.user_type == 'staff'

@login_required
@user_passes_test(is_staff)
def create_course(request):
    if request.method == 'POST':
        # Get the active academic session
        active_session = AcademicSession.objects.filter(is_active=True).first()
        if not active_session:
            messages.error(request, 'No active academic session found. Please contact the administrator.')
            return redirect('accounts:create_course')

        # Create the course first (without department/level)
        course = Course.objects.create(
            code=request.POST.get('code'),
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            credits=request.POST.get('credits'),
            semester=request.POST.get('semester'),
            academic_session=active_session,
            created_by=request.user
        )

        # Get selected departments and levels
        selected_departments = request.POST.getlist('departments')
        selected_levels = request.POST.getlist('levels')

        # Create CourseOffering records for each department-level combination
        offerings_created = 0
        for dept_id in selected_departments:
            for level_id in selected_levels:
                try:
                    department = Department.objects.get(id=dept_id)
                    level = Level.objects.get(id=level_id)
                    CourseOffering.objects.create(
                        course=course,
                        department=department,
                        level=level,
                        is_active=True
                    )
                    offerings_created += 1
                except (Department.DoesNotExist, Level.DoesNotExist):
                    continue

        if offerings_created > 0:
            messages.success(request, f'Course {course.code} created successfully with {offerings_created} department-level offerings!')
        else:
            messages.warning(request, f'Course {course.code} created but no offerings were specified.')

        return redirect('accounts:manage_courses')

    # Get academic sessions for display
    academic_sessions = AcademicSession.objects.all().order_by('-start_year')

    context = {
        'departments': Department.objects.all(),
        'academic_sessions': academic_sessions,
        'levels': Level.objects.all().order_by('order')
    }
    return render(request, 'accounts/courses/create_course.html', context)

@login_required
@user_passes_test(is_staff)
def manage_courses(request):
    department = request.user.staffprofile.department
    # Get course offerings for this staff member's department
    course_offerings = CourseOffering.objects.filter(
        department=department
    ).select_related('course', 'level').order_by('course__code')

    # Group by course for easier display
    courses_data = {}
    for offering in course_offerings:
        course_id = offering.course.id
        if course_id not in courses_data:
            courses_data[course_id] = {
                'course': offering.course,
                'offerings': []
            }
        courses_data[course_id]['offerings'].append(offering)

    context = {
        'courses_data': courses_data,
        'department': department
    }
    return render(request, 'accounts/manage_courses.html', context)


@login_required
def department_students(request):
    """View for staff to see students in their department"""

    if request.user.user_type != 'staff':
        messages.error(request, "Access denied. Staff only.")
        return redirect('dashboard:student_dashboard')
    
    try:
        staff_profile = request.user.staffprofile
        department = staff_profile.department
        
        # Get all students in the department
        students = StudentProfile.objects.filter(
            department=department
        ).select_related('user').order_by('current_level', 'user__first_name')
        
        # Group students by level
        students_by_level = {}
        for student in students:
            level = student.current_level
            if level not in students_by_level:
                students_by_level[level] = []
            students_by_level[level].append(student)


        context = {
            'department': department,
            'students_by_level': students_by_level,
            'total_students': students.count(),
              }
        return render(request, 'accounts/department_students.html', context)
        
    except StaffProfile.DoesNotExist:
        messages.error(request, "Staff profile not found. Please contact the administrator.")
        return redirect('dashboard:staff_dashboard')

@login_required
def student_detail(request, student_id):
    """Detailed view of a student for staff members"""
    if request.user.user_type != 'staff':
        messages.error(request, "Access denied. Staff only.")
        return redirect('dashboard:student_dashboard')
    
    try:
        staff_profile = request.user.staffprofile
        student = StudentProfile.objects.select_related(
            'user', 'department', 'faculty'
        ).get(id=student_id)
        
        # Ensure staff can only view students from their department
        if student.department != staff_profile.department:
            messages.error(request, "Access denied. You can only view students from your department.")
            return redirect('accounts:department_students')
        
        # Get student's course registrations
        course_registrations = CourseRegistration.objects.filter(
            student=student
        ).select_related('course').order_by('-registration_date')
        
        # Group courses by semester
        courses_by_semester = {}
        for reg in course_registrations:
            semester_key = f"{reg.course.get_semester_display()} - Level {reg.course.level}"
            if semester_key not in courses_by_semester:
                courses_by_semester[semester_key] = []
            courses_by_semester[semester_key].append(reg)
        
        context = {
            'student': student,
            'courses_by_semester': courses_by_semester,
            'total_courses': course_registrations.count(),
            'total_credits': sum(reg.course.credits for reg in course_registrations),
        }
        return render(request, 'accounts/student_detail.html', context)
        
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student not found.")
        return redirect('accounts:department_students')
    except StaffProfile.DoesNotExist:
        messages.error(request, "Staff profile not found. Please contact the administrator.")
        return redirect('dashboard:staff_dashboard')

@login_required
def school_fees(request):
    """View for school fees payment page"""
    if request.user.user_type != 'student':
        messages.error(request, "Access denied. Students only.")
        return redirect('dashboard:staff_dashboard')
    
    try:
        from .models import FeeStructure
        student = request.user.studentprofile
        current_session = AcademicSession.objects.filter(is_active=True).first()
        if not current_session:
            # Fallback to a default session if none is active
            current_session = AcademicSession.objects.filter(name="2023/2024").first()
            if not current_session:
                messages.error(request, "No active academic session found. Please contact the administrator.")
                return redirect('dashboard:student_dashboard')

        # Get payment history
        payments = PaymentTransaction.objects.filter(
            student=student
        ).order_by('-payment_date')

        # Check if student has paid for current session and semester
        current_payment = PaymentTransaction.objects.filter(
            student=student,
            session=current_session.name,
            semester=student.current_semester,
            status='success'
        ).first()

        # Get fee amount from FeeStructure
        try:
            fee_structure = FeeStructure.objects.get(
                academic_session=current_session,
                department=student.department,
                level=student.current_level
            )
            current_fees = fee_structure.amount
        except FeeStructure.DoesNotExist:
            # If no fee is defined for this combination, show 0 or a message
            current_fees = 0
            messages.warning(request, f"No fee structure found for {student.current_level.display_name} in {current_session.name}. Please contact the administrator.")
        
        context = {
            'student': student,
            'current_session': current_session.name,
            'current_session_obj': current_session,
            'current_fees': current_fees,
            'has_paid': bool(current_payment),
            'payments': payments,
        }
        return render(request, 'accounts/school_fees.html', context)
        
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('dashboard:student_dashboard')

@login_required
@require_http_methods(["POST"])
def initiate_payment(request):
    """Initialize payment with Paystack"""
    try:
        student = request.user.studentprofile
        data = json.loads(request.body)
        amount = data.get('amount')
        
        if not amount:
            return JsonResponse({'error': 'Amount is required'}, status=400)
        
        # Get current active session
        current_session = AcademicSession.objects.filter(is_active=True).first()
        if not current_session:
            current_session = AcademicSession.objects.filter(name="2023/2024").first()
        session_name = current_session.name if current_session else "2023/2024"

        # Generate unique reference (use student.id instead of matriculation_number to avoid special characters like /)
        reference = f"SF-{student.id}-{int(timezone.now().timestamp())}"

        # Initialize payment with Paystack
        url = "https://api.paystack.co/transaction/initialize"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "email": student.user.email,
            "amount": float(amount) * 100,  # Convert to kobo
            "reference": reference,
            "callback_url": request.build_absolute_uri(
                reverse('accounts:verify_payment', args=[reference])
            ),
                "metadata": {
                    "student_id": student.id,
                    "payment_type": "school_fees",
                    "session": session_name,
                    "semester": student.current_semester
                }
        }

        response = requests.post(url, headers=headers, json=data)
        response_data = response.json()

        if response_data['status']:
            # Create payment transaction record
            PaymentTransaction.objects.create(
                student=student,
                payment_type='school_fees',
                amount=amount,
                reference=reference,
                session=session_name,
                semester=student.current_semester
            )
            return JsonResponse(response_data)
        else:
            return JsonResponse({'error': 'Payment initialization failed'}, status=400)
            
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@csrf_exempt
def verify_payment(request, reference):
    """Verify payment with Paystack"""
    try:
        # Verify payment with Paystack
        url = f"https://api.paystack.co/transaction/verify/{reference}"
        headers = {
            "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"
        }
        response = requests.get(url, headers=headers)
        response_data = response.json()

        # Get payment transaction — scoped to the requesting student to prevent IDOR
        transaction = PaymentTransaction.objects.get(reference=reference, student__user=request.user)
        
        if response_data['status'] and response_data['data']['status'] == 'success':
            # Update transaction
            transaction.status = 'success'
            transaction.paystack_reference = response_data['data']['reference']
            transaction.verified_at = timezone.now()
            transaction.save()
            
            messages.success(request, "Payment verified successfully!")
        else:
            transaction.status = 'failed'
            transaction.save()
            messages.error(request, "Payment verification failed!")
        
        return redirect('accounts:school_fees')
        
    except PaymentTransaction.DoesNotExist:
        messages.error(request, "Payment transaction not found!")
        return redirect('accounts:school_fees')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('accounts:school_fees')
@login_required
def student_attendance(request):
    student = request.user
    attendance_records = Attendance.objects.filter(student=student).order_by('-date')
    context = {
        'attendance_records': attendance_records
    }
    return render(request, 'accounts/student_attendance.html', context)
@login_required
def payment_receipt(request, payment_id):
    """Generate payment receipt"""
    try:
        payment = PaymentTransaction.objects.select_related('student__user').get(
            id=payment_id,
            student__user=request.user,
            status='success'
        )
        
        context = {
            'payment': payment,
            'school_name': 'Almora Polytechnic Pantisawa',
            'school_address': 'Pantisawa, Nigeria',
        }
        return render(request, 'accounts/payment_receipt.html', context)
        
    except PaymentTransaction.DoesNotExist:
        messages.error(request, "Payment record not found!")
        return redirect('accounts:school_fees')

@login_required
def student_courses(request):
    """
    Display courses for student based on their department, level, and semester
    """
    # First check if user is a student
    if request.user.user_type != 'student':
        messages.error(request, "Access denied. Only students can view courses.")
        return redirect('dashboard:staff_dashboard')
        
    try:
        student = request.user.studentprofile

        # Get course offerings for student's department and level
        course_offerings = CourseOffering.objects.filter(
            department=student.department,
            level=student.current_level,
            course__academic_session=student.current_session,
            course__is_active=True,
            is_active=True
        ).select_related('course').order_by('course__semester', 'course__code')

        # Separate courses by semester
        first_semester_courses = [offering.course for offering in course_offerings if offering.course.semester == 'first']
        second_semester_courses = [offering.course for offering in course_offerings if offering.course.semester == 'second']
        
        # Get registered courses
        registered_courses = CourseRegistration.objects.filter(
            student=student
        ).values_list('course_id', flat=True)
        
        context = {
            'first_semester_courses': first_semester_courses,
            'second_semester_courses': second_semester_courses,
            'registered_courses': registered_courses,
            'current_semester': student.current_semester,
            'student': student
        }
        return render(request, 'accounts/courses/student_courses.html', context)
    except StudentProfile.DoesNotExist:
        messages.error(request, "Student profile not found. Please contact the administrator.")
        return redirect('dashboard:student_dashboard')


@login_required
def create_student(request):
    """Allow staff to create a new student under their department"""
    if request.user.user_type != 'staff':
        messages.error(request, "Access denied. Staff only.")
        return redirect('dashboard:student_dashboard')

    try:
        staff_profile = request.user.staffprofile
    except StaffProfile.DoesNotExist:
        messages.error(request, "Staff profile not found.")
        return redirect('dashboard:staff_dashboard')

    if request.method == 'POST':
        # Get form data
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        id_number = request.POST.get('id_number', '').strip()
        password = request.POST.get('password', '').strip()
        password_confirm = request.POST.get('password_confirm', '').strip()
        gender = request.POST.get('gender', '')
        department_id = request.POST.get('department')
        faculty_id = request.POST.get('faculty')
        level_id = request.POST.get('level')
        programme_type = request.POST.get('programme_type', 'degree')
        admission_year = request.POST.get('admission_year', '2024')
        session_id = request.POST.get('session')

        # Validation
        errors = []
        if not first_name:
            errors.append("First name is required.")
        if not last_name:
            errors.append("Last name is required.")
        if not id_number:
            errors.append("Student ID number is required.")
        if not password:
            errors.append("Password is required.")
        if password != password_confirm:
            errors.append("Passwords do not match.")
        if len(password) < 6:
            errors.append("Password must be at least 6 characters.")

        # Check if ID number already exists
        if User.objects.filter(id_number=id_number).exists():
            errors.append(f"A user with ID number '{id_number}' already exists.")

        # Check if email already exists (if provided)
        if email and User.objects.filter(email=email).exists():
            errors.append(f"A user with email '{email}' already exists.")

        if errors:
            for error in errors:
                messages.error(request, error)
        else:
            try:
                # Create username from id_number (replace / with _)
                username = id_number.replace('/', '_').lower()

                # Ensure username is unique
                base_username = username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}_{counter}"
                    counter += 1

                # Get related objects
                department = Department.objects.get(id=department_id)
                from accounts.models import Faculty
                faculty = Faculty.objects.get(id=faculty_id)
                level = Level.objects.get(id=level_id)

                # Get academic session
                session = None
                if session_id:
                    session = AcademicSession.objects.get(id=session_id)

                # Create user
                user = User(
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    email=email,
                    user_type='student',
                    id_number=id_number,
                    is_verified=True,  # Staff-created students are auto-verified
                )
                user.set_password(password)
                user.save()

                # Update the student profile that was auto-created by the signal
                try:
                    student_profile = StudentProfile.objects.get(user=user)
                    student_profile.faculty = faculty
                    student_profile.department = department
                    student_profile.current_level = level
                    student_profile.programme_type = programme_type
                    student_profile.admission_year = admission_year
                    student_profile.gender = gender
                    if session:
                        student_profile.current_session = session
                    student_profile.save()
                except StudentProfile.DoesNotExist:
                    # If signal didn't create it, create manually
                    StudentProfile.objects.create(
                        user=user,
                        faculty=faculty,
                        department=department,
                        current_level=level,
                        programme_type=programme_type,
                        admission_year=admission_year,
                        gender=gender,
                        program='BSc',
                        permanent_address='',
                        local_government='',
                        state_of_origin='',
                        cgpa=0.00,
                        current_session=session,
                    )

                messages.success(request, f"Student '{first_name} {last_name}' created successfully with ID: {id_number}")
                return redirect('accounts:department_students')

            except Department.DoesNotExist:
                messages.error(request, "Selected department not found.")
            except Level.DoesNotExist:
                messages.error(request, "Selected level not found.")
            except Exception as e:
                messages.error(request, f"Error creating student: {str(e)}")

    # GET request - show form
    from accounts.models import Faculty
    faculties = Faculty.objects.all()
    departments = Department.objects.all()
    levels = Level.objects.all().order_by('order')
    sessions = AcademicSession.objects.all().order_by('-start_year')
    active_session = AcademicSession.objects.filter(is_active=True).first()
    current_year = timezone.now().year

    context = {
        'faculties': faculties,
        'departments': departments,
        'levels': levels,
        'sessions': sessions,
        'active_session': active_session,
        'staff_department': staff_profile.department,
        'staff_faculty': staff_profile.faculty,
        'admission_years': [str(year) for year in range(current_year - 5, current_year + 2)],
        'current_year': str(current_year),
    }
    return render(request, 'accounts/create_student.html', context)