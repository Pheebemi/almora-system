"""Shared result-upload logic used by both the exam officer's direct upload flow
and the staff-facing upload flow (for staff assigned to a course by an exam officer)."""
from collections import Counter

from django.contrib import messages
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect

from .models import (
    AcademicSession, CourseOffering, CourseRegistration,
    Result, SemesterGPA, StudentProfile,
)


def get_score_limits(programme_type):
    if programme_type == 'nd':
        return 40, 60
    return 30, 70


def resolve_result_session(request):
    """Resolve the academic session to view/upload results for, from ?session= or the active session."""
    session_id = request.GET.get('session')
    if session_id:
        current_session = get_object_or_404(AcademicSession, id=session_id)
    else:
        current_session = AcademicSession.objects.filter(is_active=True).first()
    active_session = AcademicSession.objects.filter(is_active=True).first()
    is_historical = current_session != active_session
    return current_session, is_historical


def get_eligible_students(course, current_session, is_historical):
    offering_dept_levels = CourseOffering.objects.filter(course=course).values_list('department_id', 'level_id')

    student_q = Q()
    if not is_historical:
        for dept_id, level_id in offering_dept_levels:
            student_q |= Q(department_id=dept_id, current_level_id=level_id, current_session=current_session)

    student_q |= Q(
        registrations__course=course,
        registrations__academic_session=current_session,
        registrations__status='registered'
    )
    student_q |= Q(
        results__course=course,
        results__academic_session=current_session
    )

    return StudentProfile.objects.filter(student_q).distinct().select_related(
        'user', 'current_level', 'department'
    ).order_by('user__id_number')


def recalculate_gpas(course, current_session):
    students_with_results = Result.objects.filter(
        course=course, academic_session=current_session
    ).values_list('student_id', flat=True).distinct()

    gpa_updated = 0
    for student_id in students_with_results:
        try:
            student_profile = StudentProfile.objects.get(id=student_id)
            semester_gpa, _ = SemesterGPA.objects.get_or_create(
                student=student_profile,
                academic_session=current_session,
                semester=course.semester,
                defaults={'level': student_profile.current_level},
            )
            semester_gpa.calculate_gpa()
            semester_gpa.calculate_cgpa()
            semester_gpa.save()
            gpa_updated += 1
        except Exception as e:
            print(f"Error calculating GPA for student {student_id}: {e}")
    return gpa_updated


def save_uploaded_results(request, course, current_session, all_students, uploaded_by):
    """Save POSTed test/exam scores for all_students. Returns (saved_count, errors, gpa_updated)."""
    saved_count = 0
    errors = []
    for student in all_students:
        test_score = request.POST.get(f"test_{student.id}", '').strip()
        exam_score = request.POST.get(f"exam_{student.id}", '').strip()

        if not test_score and not exam_score:
            continue

        try:
            test_val = float(test_score) if test_score else 0
            exam_val = float(exam_score) if exam_score else 0

            programme_type = student.programme_type
            max_test, max_exam = get_score_limits(programme_type)

            if test_val < 0 or test_val > max_test:
                errors.append(f"{student.user.get_full_name()} ({programme_type.upper()}): Test score must be 0-{max_test}")
                continue
            if exam_val < 0 or exam_val > max_exam:
                errors.append(f"{student.user.get_full_name()} ({programme_type.upper()}): Exam score must be 0-{max_exam}")
                continue

            offering = CourseOffering.objects.filter(course=course, department=student.department).first()
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
                    'uploaded_by': uploaded_by,
                }
            )
            # update_or_create doesn't reliably trigger save() logic (grade calculation),
            # so call save() explicitly to force recalculation.
            result.save()
            saved_count += 1
        except (ValueError, TypeError):
            errors.append(f"{student.user.get_full_name()}: Invalid score value")

    gpa_updated = recalculate_gpas(course, current_session) if saved_count > 0 else 0
    return saved_count, errors, gpa_updated


def build_students_data(all_students, course, current_session):
    registered_student_ids = set(
        CourseRegistration.objects.filter(course=course, status='registered').values_list('student_id', flat=True)
    )
    results_map = {r.student_id: r for r in Result.objects.filter(course=course, academic_session=current_session)}

    students_data = []
    for student in all_students:
        result = results_map.get(student.id)
        p_type = student.programme_type
        max_test, max_exam = get_score_limits(p_type)
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

    dominant_type = 'degree'
    if all_students.exists():
        type_counts = Counter(s.programme_type for s in all_students)
        dominant_type = type_counts.most_common(1)[0][0]

    return {
        'students_data': students_data,
        'total_students': all_students.count(),
        'registered_count': len(registered_student_ids),
        'results_completed': len(results_map),
        'dominant_type': dominant_type,
        'max_test': 40 if dominant_type == 'nd' else 30,
        'max_exam': 60 if dominant_type == 'nd' else 70,
    }


def handle_result_upload(request, course, redirect_url_name, redirect_args=None, locked=False, locked_message=None):
    """Handle GET (build context) and POST (save + redirect) for a single course's result upload.

    Returns an HttpResponseRedirect for POST requests, or a context dict (without 'course')
    ready to be merged into the render context for GET requests.
    """
    current_session, is_historical = resolve_result_session(request)
    all_students = get_eligible_students(course, current_session, is_historical)

    if request.method == 'POST':
        if locked:
            messages.error(request, locked_message or "Your result upload access has been locked by the exam officer.")
        else:
            saved_count, errors, gpa_updated = save_uploaded_results(
                request, course, current_session, all_students, request.user
            )
            for err in errors:
                messages.warning(request, err)
            if saved_count > 0:
                messages.success(request, f"Successfully saved {saved_count} result(s) for {course.code}!")
                if gpa_updated > 0:
                    messages.info(request, f"GPA/CGPA updated for {gpa_updated} student(s).")
        return redirect(redirect_url_name, *(redirect_args or []))

    context = {'current_session': current_session, 'locked': locked}
    context.update(build_students_data(all_students, course, current_session))
    return context
