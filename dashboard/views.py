from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import StudentProfile, AcademicRecord, Course, CourseOffering, AcademicSession
from .decorators import student_required, staff_required
from datetime import datetime
from django.contrib import messages
from .models import SupportRequest, Notification
from .forms import SupportForm
from django.contrib.auth.decorators import login_required

# Create your views here.
@student_required
def student_dashboard(request):
    try:
        profile = StudentProfile.objects.get(user=request.user)
    except StudentProfile.DoesNotExist:
        messages.error(request, "Your student profile has not been set up. Please contact the admin.")
        return redirect('student_login')
    
    # Check if profile is complete
    if not profile.is_profile_complete:
        messages.warning(request, "Please update your profile information to continue to your dashboard.")
        return redirect('accounts:edit_student_profile')

    # Get current academic session
    current_session = profile.current_session
    session_name = f"{current_session.start_year}/{current_session.end_year}" if current_session else "2023/2024"

    # Get registered courses for current session
    from accounts.models import CourseRegistration
    registered_courses = CourseRegistration.objects.filter(
        student=profile,
        course__academic_session=current_session
    ).select_related('course')

    # Calculate stats
    total_registered = registered_courses.count()
    total_credits = sum(reg.course.credits for reg in registered_courses)
    completed_courses = registered_courses.filter(status='completed').count()
    current_semester = profile.current_semester.title()

    # Get recent notifications
    notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]

    # Get upcoming deadlines (if any)
    # This could be enhanced with actual deadline data

    context = {
        'profile': profile,
        'session_name': session_name,
        'total_registered': total_registered,
        'total_credits': total_credits,
        'completed_courses': completed_courses,
        'current_semester': current_semester,
        'notifications': notifications,
        'registered_courses': registered_courses[:3],  # Show recent 3 courses
        'current_year': datetime.now().year,
    }
    return render(request, 'dashboard/student-dashboard.html', context)

@student_required
def courses(request):
    profile = StudentProfile.objects.get(user=request.user)
    record = AcademicRecord.objects.filter(student=profile)
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    courses = [record.course for record in record if record.course]
    count = len(courses)
    context = {
        'record': record,
        'profile': profile,
        'current_year' : current_year,
        'count': count,
        'notifications': notifications,
    }
    return render(request, 'dashboard/courses.html', context)

@student_required
def timetable(request):
    profile = StudentProfile.objects.get(user=request.user)
    record = AcademicRecord.objects.filter(student=profile)
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    context = {
        'record': record,
        'notifications': notifications,
    }
    return render(request, 'dashboard/timetable.html', context)

@staff_required
def staff_dashboard(request):
    staff_profile = request.user.staffprofile
    department = staff_profile.department

    # Calculate department statistics
    total_students = StudentProfile.objects.filter(department=department).count()
    active_students = StudentProfile.objects.filter(
        department=department,
        current_session__is_active=True
    ).count()

    total_courses = CourseOffering.objects.filter(department=department).values('course').distinct().count()
    active_courses = CourseOffering.objects.filter(
        department=department,
        course__is_active=True
    ).values('course').distinct().count()

    # Get students by level
    level_100_count = StudentProfile.objects.filter(department=department, current_level__name='100').count()
    level_200_count = StudentProfile.objects.filter(department=department, current_level__name='200').count()
    level_300_count = StudentProfile.objects.filter(department=department, current_level__name='300').count()
    level_400_count = StudentProfile.objects.filter(department=department, current_level__name='400').count()

    # Get recent courses created by this staff (via offerings in their department)
    recent_courses = Course.objects.filter(
        offerings__department=department,
        created_by=request.user
    ).distinct().order_by('-created_at')[:3]

    # Get notifications
    notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]

    # Get current academic session
    current_session = AcademicSession.objects.filter(is_active=True).first()
    session_name = f"{current_session.start_year}/{current_session.end_year}" if current_session else "2023/2024"

    context = {
        'staff_profile': staff_profile,
        'department': department,
        'session_name': session_name,
        'total_students': total_students,
        'active_students': active_students,
        'total_courses': total_courses,
        'active_courses': active_courses,
        'level_100_count': level_100_count,
        'level_200_count': level_200_count,
        'level_300_count': level_300_count,
        'level_400_count': level_400_count,
        'recent_courses': recent_courses,
        'notifications': notifications,
    }
    return render(request, 'dashboard/staff-dashboard.html', context)

@login_required
def support(request):
    if request.method == 'POST':
        form = SupportForm(request.POST)
        if form.is_valid():
            support_request = form.save(commit=False)
            support_request.user = request.user
            support_request.save()
            messages.success(request, 'Your support request has been submitted successfully.')
            
            # Redirect based on user role
            if request.user.user_type == 'staff':
                return redirect('dashboard:staff_dashboard')
            else:
                return redirect('dashboard:student_dashboard')
        else:
            messages.error(request, 'There was an error submitting your support request. Please try again.')
    else:
        form = SupportForm()
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    return render(request, 'dashboard/support.html', {'form': form, 'notifications': notifications})

@login_required
def notifications(request):
    # Get all notifications (both read and unread), sorted by unread first, then by date
    all_notifications = Notification.objects.filter(user=request.user).order_by('is_read', '-created_at')
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()

    context = {
        'notifications': all_notifications,
        'count': unread_count,
    }
    return render(request, 'dashboard/notifications.html', context)

@login_required
def mark_notification_as_read(request, notification_id):
    notification = Notification.objects.get(id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()

    return redirect('dashboard:notifications')

@login_required
def support_request_detail(request, support_request_id):
    support_request = get_object_or_404(SupportRequest, id=support_request_id, user=request.user)
    return render(request, 'dashboard/support_request_detail.html', {'support_request': support_request})