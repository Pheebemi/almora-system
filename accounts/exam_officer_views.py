from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django_ratelimit.decorators import ratelimit
from .models import (
    User, ExamOfficerProfile, Result, SemesterGPA,
    Course, CourseOffering, CourseRegistration, StudentProfile,
    AcademicSession, Level, Department, Faculty
)


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

        user = authenticate(request, username=username, password=password)
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
    
    # Get the session from the URL parameter, default to active session
    session_id = request.GET.get('session')
    if session_id:
        current_session = get_object_or_404(AcademicSession, id=session_id)
    else:
        current_session = AcademicSession.objects.filter(is_active=True).first()

    # Verify this course belongs to officer's assigned programme types
    valid_offerings = CourseOffering.objects.filter(
        course=course,
        department__faculty__programme_type__in=assigned_types
    )
    if not valid_offerings.exists():
        messages.error(request, "You are not authorized to upload results for this course.")
        return redirect('accounts:exam_officer_select_course')

    # Determine if this is a historical session
    active_session = AcademicSession.objects.filter(is_active=True).first()
    is_historical = current_session != active_session

    # Get all departments and levels that offer this course
    offering_dept_levels = valid_offerings.values_list('department_id', 'level_id')

    # Build query to get the correct students
    from django.db.models import Q
    student_q = Q()
    
    if not is_historical:
        # For the active session, pull everyone currently in the level AND session
        for dept_id, level_id in offering_dept_levels:
            student_q |= Q(department_id=dept_id, current_level_id=level_id, current_session=current_session)
            
    # Always include students who actually registered or already have results for this course/session
    student_q |= Q(
        registrations__course=course, 
        registrations__academic_session=current_session,
        registrations__status='registered'
    )
    student_q |= Q(
        results__course=course,
        results__academic_session=current_session
    )

    all_students = StudentProfile.objects.filter(
        student_q
    ).distinct().select_related('user', 'current_level', 'department').order_by('user__id_number')

    # Get set of registered student IDs for this course
    registered_student_ids = set(
        CourseRegistration.objects.filter(
            course=course,
            status='registered'
        ).values_list('student_id', flat=True)
    )

    if request.method == 'POST':
        saved_count = 0
        errors = []
        for student in all_students:
            test_key = f"test_{student.id}"
            exam_key = f"exam_{student.id}"

            test_score = request.POST.get(test_key, '').strip()
            exam_score = request.POST.get(exam_key, '').strip()

            if not test_score and not exam_score:
                continue  # Skip students with no scores entered

            try:
                test_val = float(test_score) if test_score else 0
                exam_val = float(exam_score) if exam_score else 0

                # Get programme-specific limits
                programme_type = student.programme_type
                if programme_type == 'nd':
                    max_test, max_exam = 40, 60
                else: # hnd, degree, etc.
                    max_test, max_exam = 30, 70

                if test_val < 0 or test_val > max_test:
                    errors.append(f"{student.user.get_full_name()} ({programme_type.upper()}): Test score must be 0-{max_test}")
                    continue
                if exam_val < 0 or exam_val > max_exam:
                    errors.append(f"{student.user.get_full_name()} ({programme_type.upper()}): Exam score must be 0-{max_exam}")
                    continue

                # Get the level from the course offering for this student
                offering = CourseOffering.objects.filter(
                    course=course,
                    department=student.department
                ).first()
                level = offering.level if offering else student.current_level

                result, created = Result.objects.update_or_create(
                    student=student,
                    course=course,
                    academic_session=current_session,
                    defaults={
                        'semester': course.semester,
                        'level': level,
                        'test_score': test_val,
                        'exam_score': exam_val,
                        'uploaded_by': request.user,
                    }
                )
                
                # IMPORTANT: update_or_create doesn't always trigger custom save() logic 
                # (like calculate_grade) if fields don't seem to change in the way Django expects,
                # or it might use bulk updates. We must call save() explicitly to force recalculation.
                result.save()
                
                saved_count += 1
            except (ValueError, TypeError) as e:
                errors.append(f"{student.user.get_full_name()}: Invalid score value")

        if errors:
            for err in errors:
                messages.warning(request, err)
        if saved_count > 0:
            messages.success(request, f"Successfully saved {saved_count} result(s) for {course.code}!")

            # Auto-calculate GPA/CGPA for all students who got results
            students_with_results = Result.objects.filter(
                course=course,
                academic_session=current_session
            ).values_list('student_id', flat=True).distinct()

            gpa_updated = 0
            for student_id in students_with_results:
                try:
                    student_profile = StudentProfile.objects.get(id=student_id)
                    # Get or create SemesterGPA for this student/session/semester
                    semester_gpa, created = SemesterGPA.objects.get_or_create(
                        student=student_profile,
                        academic_session=current_session,
                        semester=course.semester,
                        defaults={
                            'level': student_profile.current_level,
                        }
                    )
                    # Calculate GPA for this semester
                    semester_gpa.calculate_gpa()
                    # Calculate cumulative GPA
                    semester_gpa.calculate_cgpa()
                    semester_gpa.save()

                    gpa_updated += 1
                except Exception as e:
                    print(f"Error calculating GPA for student {student_id}: {e}")

            if gpa_updated > 0:
                messages.info(request, f"GPA/CGPA updated for {gpa_updated} student(s).")

        return redirect('accounts:exam_officer_upload_results', course_id=course.id)

    # Get existing results for pre-filling the form
    results_map = {}
    existing_results = Result.objects.filter(
        course=course,
        academic_session=current_session
    )
    for r in existing_results:
        results_map[r.student_id] = r

    # Build detailed context for each student
    students_data = []
    for student in all_students:
        result = results_map.get(student.id)
        
        # Get student-specific limits
        p_type = student.programme_type
        if p_type == 'nd':
            max_test, max_exam = 40, 60
        else:
            max_test, max_exam = 30, 70
            
        students_data.append({
            'student': student,
            'is_registered': student.id in registered_student_ids,
            'has_result': result is not None,
            'test_score': result.test_score if result else '',
            'exam_score': result.exam_score if result else '',
            'total_score': result.total_score if result else None,
            'grade': result.grade if result else None,
            'programme_type': p_type,
            'max_test': max_test,
            'max_exam': max_exam,
        })

    # Determine dominant programme type for UI hints
    dominant_type = 'degree'
    if all_students.exists():
        from collections import Counter
        type_counts = Counter(s.programme_type for s in all_students)
        dominant_type = type_counts.most_common(1)[0][0]

    context = {
        'course': course,
        'current_session': current_session,
        'students_data': students_data,
        'total_students': all_students.count(),
        'registered_count': len(registered_student_ids),
        'results_completed': len(results_map),
        'dominant_type': dominant_type,
        'max_test': 40 if dominant_type == 'nd' else 30,
        'max_exam': 60 if dominant_type == 'nd' else 70,
    }
    return render(request, 'accounts/exam_officer/upload_results.html', context)


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
