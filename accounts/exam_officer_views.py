from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.db.models import Q
from django.core.paginator import Paginator
from django_ratelimit.decorators import ratelimit
from .models import (
    User, ExamOfficerProfile, Result, SemesterGPA,
    Course, CourseOffering, CourseRegistration, StudentProfile,
    AcademicSession, Level, Department, Faculty,
    StaffProfile, CourseStaffAssignment,
)
from .utils import resolve_login_username
from .result_utils import handle_result_upload


def is_exam_officer(user):
    return user.is_authenticated and user.user_type == 'exam_officer'


@ratelimit(key='ip', rate='5/m', method='POST', block=False)
@csrf_exempt
def exam_officer_login(request):
    """Login page for exam officers"""
    if request.method == 'POST':
        if getattr(request, 'limited', False):
            messages.error(request, "Too many login attempts. Please wait a minute and try again.")
            return render(request, 'accounts/exam_officer/login.html', status=429)

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=resolve_login_username(username), password=password)
        if user is not None:
            if user.is_verified:
                if user.user_type == 'exam_officer':
                    login(request, user)
                    messages.success(request, f"Welcome, {user.get_full_name()}!")
                    return redirect('accounts:exam_officer_dashboard')
                else:
                    messages.error(request, "Only Exam Officers are allowed to log in here.")
            else:
                messages.warning(request, 'Your account is not verified. Contact the admin.')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/exam_officer/login.html')


@login_required
@user_passes_test(is_exam_officer)
def exam_officer_dashboard(request):
    """Dashboard for exam officers"""
    officer = request.user.examofficerprofile

    # Get assigned programme types
    assigned_types = officer.assigned_programme_types

    # Get current academic session
    current_session = AcademicSession.objects.filter(is_active=True).first()
    session_name = f"{current_session.start_year}/{current_session.end_year}" if current_session else "N/A"

    # Stats for assigned programme types
    total_courses = Course.objects.filter(
        offerings__department__faculty__programme_type__in=assigned_types,
        academic_session=current_session
    ).distinct().count() if current_session and assigned_types else 0

    total_results_uploaded = Result.objects.filter(
        uploaded_by=request.user,
        academic_session=current_session
    ).count() if current_session else 0

    # Get courses that need results (have registered students but no results yet)
    pending_courses = 0
    if current_session and assigned_types:
        courses_with_registrations = Course.objects.filter(
            offerings__department__faculty__programme_type__in=assigned_types,
            academic_session=current_session,
            is_active=True,
            registrations__status='registered'
        ).distinct()
        for course in courses_with_registrations:
            registered_count = CourseRegistration.objects.filter(
                course=course, status='registered'
            ).count()
            results_count = Result.objects.filter(
                course=course, academic_session=current_session
            ).count()
            if results_count < registered_count:
                pending_courses += 1

    # Recent uploads
    recent_results = Result.objects.filter(
        uploaded_by=request.user
    ).select_related('student__user', 'course').order_by('-uploaded_at')[:10]

    context = {
        'officer': officer,
        'session_name': session_name,
        'current_session': current_session,
        'assigned_types': assigned_types,
        'total_courses': total_courses,
        'total_results_uploaded': total_results_uploaded,
        'pending_courses': pending_courses,
        'recent_results': recent_results,
    }
    return render(request, 'accounts/exam_officer/dashboard.html', context)


@login_required
@user_passes_test(is_exam_officer)
def select_course(request):
    """Step 1: Select a course to upload results for"""
    officer = request.user.examofficerprofile
    assigned_types = officer.assigned_programme_types

    current_session = AcademicSession.objects.filter(is_active=True).first()

    # Get filter params
    filter_session = request.GET.get('session', '')
    filter_semester = request.GET.get('semester', '')
    filter_programme = request.GET.get('programme', '')
    filter_level = request.GET.get('level', '')
    search_query = request.GET.get('q', '').strip()

    # Use selected session or current
    if filter_session:
        selected_session = get_object_or_404(AcademicSession, id=filter_session)
    else:
        selected_session = current_session

    course_data = []
    
    active_session = AcademicSession.objects.filter(is_active=True).first()
    is_historical = selected_session != active_session
    
    # Check if user has actively searched using specific filters (not just session)
    has_specific_filter = bool(filter_semester or filter_programme or filter_level or search_query)
    
    if has_specific_filter:
        # Get courses for assigned programme types - always alphabetical by code
        courses = Course.objects.filter(
            offerings__department__faculty__programme_type__in=assigned_types,
            is_active=True
        ).distinct().order_by('code')

        if filter_semester:
            courses = courses.filter(semester=filter_semester)

        if filter_programme and filter_programme in assigned_types:
            courses = courses.filter(
                offerings__department__faculty__programme_type=filter_programme
            ).distinct()

        if filter_level:
            try:
                level_id = int(filter_level)
                courses = courses.filter(
                    offerings__level__id=level_id
                ).distinct()
            except ValueError:
                pass

        # Re-apply ordering after distinct() to guarantee alphabetical order
        courses = courses.order_by('code')

        # Apply search query
        if search_query:
            from django.db.models import Q as SearchQ
            courses = courses.filter(
                SearchQ(code__icontains=search_query) | SearchQ(title__icontains=search_query)
            )

        # Build course data with registration counts and result status
        from django.db.models import Q
        for course in courses:
            # Get offerings to find eligible students
            course_offerings = CourseOffering.objects.filter(course=course)
            
            if not is_historical:
                # Active session: calculate potential eligible from current level AND session
                student_q = Q()
                for offering in course_offerings:
                    student_q |= Q(department=offering.department, current_level=offering.level, current_session=selected_session)
                
                cohort_size = StudentProfile.objects.filter(student_q).count() if course_offerings.exists() else 0
            else:
                # Historical session: cohort_size based on current level is meaningless
                cohort_size = 0
            
            registered = CourseRegistration.objects.filter(
                course=course, status='registered', academic_session=selected_session
            ).count()
            
            results_done = Result.objects.filter(
                course=course, academic_session=selected_session
            ).count()
            
            # Use max to get the realistic denominator
            total_eligible = max(registered, results_done, cohort_size)
            
            course_data.append({
                'course': course,
                'registered': registered,
                'total_eligible': total_eligible,
                'results_done': results_done,
                'is_complete': results_done >= total_eligible and total_eligible > 0,
            })

    # Pagination
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    page = request.GET.get('page', 1)
    paginator = Paginator(course_data, 25)  # 25 courses per page
    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    # Get available filters
    available_sessions = AcademicSession.objects.all().order_by('-start_year')
    available_levels = Level.objects.filter(
        programme_type__in=assigned_types
    ).order_by('order')

    context = {
        'course_data': page_obj,
        'page_obj': page_obj,
        'paginator': paginator,
        'available_sessions': available_sessions,
        'available_levels': available_levels,
        'assigned_types': assigned_types,
        'current_session': current_session,
        'selected_session': selected_session,
        'filter_session': filter_session,
        'filter_semester': filter_semester,
        'filter_programme': filter_programme,
        'filter_level': filter_level,
        'search_query': search_query,
    }
    return render(request, 'accounts/exam_officer/select_course.html', context)


@login_required
@user_passes_test(is_exam_officer)
def upload_results(request, course_id):
    """Step 2: View all department students and enter/edit scores"""
    officer = request.user.examofficerprofile
    assigned_types = officer.assigned_programme_types

    course = get_object_or_404(Course, id=course_id)

    # Verify this course belongs to officer's assigned programme types
    valid_offerings = CourseOffering.objects.filter(
        course=course,
        department__faculty__programme_type__in=assigned_types
    )
    if not valid_offerings.exists():
        messages.error(request, "You are not authorized to upload results for this course.")
        return redirect('accounts:exam_officer_select_course')

    result = handle_result_upload(
        request, course,
        redirect_url_name='accounts:exam_officer_upload_results',
        redirect_args=[course.id],
    )
    if not isinstance(result, dict):
        return result  # POST -> redirect

    context = {
        'course': course,
        'back_url': reverse('accounts:exam_officer_select_course'),
        **result,
    }
    return render(request, 'accounts/courses/result_upload.html', context)


@login_required
@user_passes_test(is_exam_officer)
def view_student_gpas(request):
    """View student GPA/CGPA records"""
    officer = request.user.examofficerprofile
    assigned_types = officer.assigned_programme_types

    # Get filter params
    filter_session = request.GET.get('session', '')
    filter_level = request.GET.get('level', '')
    filter_department = request.GET.get('department', '')

    current_session = AcademicSession.objects.filter(is_active=True).first()

    # Use selected session or current
    if filter_session:
        selected_session = get_object_or_404(AcademicSession, id=filter_session)
    else:
        selected_session = current_session

    # Get all SemesterGPA records for the selected session
    gpa_records = SemesterGPA.objects.filter(
        academic_session=selected_session,
        student__programme_type__in=assigned_types
    ).select_related(
        'student__user', 'student__department', 'student__current_level',
        'level', 'academic_session'
    ).order_by('student__department__name', 'student__user__last_name')

    if filter_level:
        gpa_records = gpa_records.filter(level_id=filter_level)

    if filter_department:
        gpa_records = gpa_records.filter(student__department_id=filter_department)

    # Group by student for display
    from collections import OrderedDict
    student_gpas = OrderedDict()
    for record in gpa_records:
        student_id = record.student_id
        if student_id not in student_gpas:
            student_gpas[student_id] = {
                'student': record.student,
                'first_semester': None,
                'second_semester': None,
                'cgpa': 0.00,
            }
        if record.semester == 'first':
            student_gpas[student_id]['first_semester'] = record
        elif record.semester == 'second':
            student_gpas[student_id]['second_semester'] = record
        
        # Use the latest record to get the most up-to-date CGPA and classification
        if not student_gpas[student_id].get('latest_record') or record.semester == 'second':
            student_gpas[student_id]['latest_record'] = record
            student_gpas[student_id]['cgpa'] = record.cgpa

    # Get available filters
    available_sessions = AcademicSession.objects.all().order_by('-start_year')
    available_levels = Level.objects.filter(
        programme_type__in=assigned_types
    ).order_by('order')
    available_departments = Department.objects.filter(
        faculty__programme_type__in=assigned_types
    ).order_by('name')

    context = {
        'student_gpas': student_gpas,
        'available_sessions': available_sessions,
        'available_levels': available_levels,
        'available_departments': available_departments,
        'selected_session': selected_session,
        'filter_session': filter_session,
        'filter_level': filter_level,
        'filter_department': filter_department,
        'total_records': len(student_gpas),
    }
    return render(request, 'accounts/exam_officer/student_gpas.html', context)


@login_required
@user_passes_test(is_exam_officer)
def department_results_sheet(request):
    officer = request.user.examofficerprofile
    assigned_types = officer.assigned_programme_types

    available_sessions = AcademicSession.objects.all().order_by('-start_year')
    available_departments = Department.objects.filter(
        faculty__programme_type__in=assigned_types
    ).select_related('faculty').order_by('name')
    available_levels = Level.objects.filter(
        programme_type__in=assigned_types, is_active=True
    ).order_by('order')

    session_id = request.GET.get('session')
    dept_id = request.GET.get('department')
    level_id = request.GET.get('level')
    filter_semester = request.GET.get('semester', 'both')

    selected_session = AcademicSession.objects.filter(is_active=True).first()
    if session_id:
        selected_session = AcademicSession.objects.filter(id=session_id).first() or selected_session

    student_results = []
    selected_department = None
    selected_level = None

    if dept_id and level_id:
        selected_department = Department.objects.filter(id=dept_id).first()
        selected_level = Level.objects.filter(id=level_id).first()

        if selected_department and selected_level:
            students = StudentProfile.objects.filter(
                department=selected_department,
                current_level=selected_level,
                current_session=selected_session,
            ).select_related('user').order_by('user__last_name', 'user__first_name')

            for student in students:
                result_qs = Result.objects.filter(
                    student=student,
                    academic_session=selected_session,
                ).select_related('course')

                if filter_semester in ('first', 'second'):
                    result_qs = result_qs.filter(semester=filter_semester)

                passed = [f"{r.course.code}({r.grade})" for r in result_qs if r.grade != 'F']
                failed = [f"{r.course.code}({r.grade})" for r in result_qs if r.grade == 'F']

                student_results.append({
                    'student': student,
                    'passed': ', '.join(passed) if passed else '—',
                    'failed': ', '.join(failed) if failed else 'NIL',
                })

    return render(request, 'accounts/exam_officer/department_results_sheet.html', {
        'available_sessions': available_sessions,
        'available_departments': available_departments,
        'available_levels': available_levels,
        'selected_session': selected_session,
        'selected_department': selected_department,
        'selected_level': selected_level,
        'filter_department': dept_id or '',
        'filter_level': level_id or '',
        'filter_semester': filter_semester,
        'student_results': student_results,
        'total_students': len(student_results),
    })


@login_required
@user_passes_test(is_exam_officer)
def manage_staff(request):
    """List staff in the officer's assigned programme types and manage their
    course result-upload assignments and lock status."""
    officer = request.user.examofficerprofile
    assigned_types = officer.assigned_programme_types

    search_query = request.GET.get('q', '').strip()
    filter_department = request.GET.get('department', '')

    staff_qs = StaffProfile.objects.filter(
        department__faculty__programme_type__in=assigned_types
    ).select_related('user', 'department', 'faculty').prefetch_related('course_assignments__course')

    if filter_department:
        staff_qs = staff_qs.filter(department_id=filter_department)

    if search_query:
        staff_qs = staff_qs.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(staff_id__icontains=search_query)
        )

    staff_qs = staff_qs.order_by('user__last_name', 'user__first_name')

    paginator = Paginator(staff_qs, 25)
    page_obj = paginator.get_page(request.GET.get('page'))

    available_courses = Course.objects.filter(
        offerings__department__faculty__programme_type__in=assigned_types,
        is_active=True
    ).distinct().order_by('code')

    available_departments = Department.objects.filter(
        faculty__programme_type__in=assigned_types
    ).order_by('name')

    context = {
        'staff_list': page_obj,
        'page_obj': page_obj,
        'available_courses': available_courses,
        'available_departments': available_departments,
        'search_query': search_query,
        'filter_department': filter_department,
    }
    return render(request, 'accounts/exam_officer/manage_staff.html', context)


@login_required
@user_passes_test(is_exam_officer)
def assign_staff_course(request, staff_id):
    """Assign a course to a staff member so they can upload results for it."""
    officer = request.user.examofficerprofile
    assigned_types = officer.assigned_programme_types
    staff = get_object_or_404(
        StaffProfile, id=staff_id, department__faculty__programme_type__in=assigned_types
    )

    if request.method == 'POST':
        course = get_object_or_404(
            Course, id=request.POST.get('course_id'),
            offerings__department__faculty__programme_type__in=assigned_types
        )
        assignment, created = CourseStaffAssignment.objects.get_or_create(
            staff=staff, course=course,
            defaults={'assigned_by': request.user}
        )
        if created:
            messages.success(request, f"{staff.user.get_full_name()} assigned to {course.code}.")
        else:
            messages.info(request, f"{staff.user.get_full_name()} is already assigned to {course.code}.")

    return redirect('accounts:exam_officer_manage_staff')


@login_required
@user_passes_test(is_exam_officer)
def unassign_staff_course(request, staff_id, assignment_id):
    """Remove a staff member's assignment to a course."""
    officer = request.user.examofficerprofile
    assigned_types = officer.assigned_programme_types
    staff = get_object_or_404(
        StaffProfile, id=staff_id, department__faculty__programme_type__in=assigned_types
    )
    assignment = get_object_or_404(CourseStaffAssignment, id=assignment_id, staff=staff)

    if request.method == 'POST':
        course_code = assignment.course.code
        assignment.delete()
        messages.success(request, f"Removed {staff.user.get_full_name()}'s assignment to {course_code}.")

    return redirect('accounts:exam_officer_manage_staff')


@login_required
@user_passes_test(is_exam_officer)
def toggle_staff_lock(request, staff_id):
    """Lock or unlock a staff member's ability to add/edit results for their assigned courses."""
    officer = request.user.examofficerprofile
    assigned_types = officer.assigned_programme_types
    staff = get_object_or_404(
        StaffProfile, id=staff_id, department__faculty__programme_type__in=assigned_types
    )

    if request.method == 'POST':
        staff.results_locked = not staff.results_locked
        staff.save(update_fields=['results_locked'])
        if staff.results_locked:
            messages.success(request, f"Result upload locked for {staff.user.get_full_name()}.")
        else:
            messages.success(request, f"Result upload unlocked for {staff.user.get_full_name()}.")

    return redirect('accounts:exam_officer_manage_staff')
