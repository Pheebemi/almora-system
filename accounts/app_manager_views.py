"""
Application Manager Views
Handles all views related to application management functionality
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django_ratelimit.decorators import ratelimit
from django.db.models import Q, Count, Avg, Sum
from django.core.paginator import Paginator
from core.models import Applicant, ScreeningForm, ScreeningPayment
from dashboard.models import Notification
from .models import ApplicationActivity, ApplicationNote, User
from datetime import datetime, timedelta
import json


def is_application_manager(user):
    """Check if user is an application manager"""
    return user.is_authenticated and user.user_type == 'application_manager'


@login_required
@user_passes_test(is_application_manager, login_url='/applicant/')
def app_manager_dashboard(request):
    """Application Manager Dashboard with statistics"""

    # Get statistics
    total_applicants = Applicant.objects.count()
    pending_applicants = Applicant.objects.filter(status='pending_review').count()
    admitted_applicants = Applicant.objects.filter(status='approved').count()
    rejected_applicants = Applicant.objects.filter(status='rejected').count()

    # Payment statistics
    total_payments = ScreeningPayment.objects.filter(status='success').count()
    payment_amount = ScreeningPayment.objects.filter(status='success').aggregate(
        total=Sum('amount')
    )['total'] or 0

    # Document verification stats
    total_forms = ScreeningForm.objects.count()
    pending_documents = ScreeningForm.objects.filter(
        Q(waec_result_status='pending') |
        Q(jamb_result_slip_status='pending') |
        Q(passport_photo_status='pending') |
        Q(birth_certificate_status='pending')
    ).count()

    # Recent activity
    recent_activities = ApplicationActivity.objects.select_related(
        'applicant__user', 'manager'
    )[:10]

    # Applications by program (for chart)
    applications_by_program = Applicant.objects.values(
        'programs__name'
    ).annotate(
        count=Count('id')
    ).order_by('-count')[:10]

    # Recent applications (last 7 days)
    week_ago = datetime.now() - timedelta(days=7)
    new_applicants = Applicant.objects.filter(
        user__date_joined__gte=week_ago
    ).count()

    context = {
        'total_applicants': total_applicants,
        'pending_applicants': pending_applicants,
        'admitted_applicants': admitted_applicants,
        'rejected_applicants': rejected_applicants,
        'total_payments': total_payments,
        'payment_amount': payment_amount,
        'total_forms': total_forms,
        'pending_documents': pending_documents,
        'recent_activities': recent_activities,
        'applications_by_program': list(applications_by_program),
        'new_applicants': new_applicants,
    }

    return render(request, 'app_manager/dashboard.html', context)


@login_required
@user_passes_test(is_application_manager, login_url='/applicant/')
def applicants_list(request):
    """List all applicants with filters and search"""

    # Get all applicants
    applicants = Applicant.objects.select_related(
        'user', 'programs'
    ).all()

    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        applicants = applicants.filter(
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(user__email__icontains=search_query) |
            Q(phone_number__icontains=search_query)
        )

    # Filters
    status_filter = request.GET.get('status', '')
    if status_filter:
        applicants = applicants.filter(status=status_filter)

    course_filter = request.GET.get('course', '')
    if course_filter:
        applicants = applicants.filter(programs__id=course_filter)

    state_filter = request.GET.get('state', '')
    if state_filter:
        applicants = applicants.filter(state=state_filter)

    payment_filter = request.GET.get('payment', '')
    if payment_filter == 'paid':
        applicants = applicants.filter(screening_payments__status='success')
    elif payment_filter == 'unpaid':
        applicants = applicants.exclude(screening_payments__status='success')

    # Pagination
    paginator = Paginator(applicants, 25)  # 25 applicants per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Get unique courses and states for filters
    from core.models import Program
    from accounts.state import NIGERIA_STATES_AND_LGAS

    courses = Program.objects.all()
    states = list(NIGERIA_STATES_AND_LGAS.keys())

    context = {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter,
        'course_filter': course_filter,
        'state_filter': state_filter,
        'payment_filter': payment_filter,
        'courses': courses,
        'states': states,
    }

    return render(request, 'app_manager/applicants_list.html', context)


@login_required
@user_passes_test(is_application_manager, login_url='/applicant/')
def applicant_detail(request, applicant_id):
    """Detailed view of a single applicant"""

    applicant = get_object_or_404(
        Applicant.objects.select_related('user', 'programs'),
        id=applicant_id
    )

    # Get screening form if exists
    try:
        screening_form = ScreeningForm.objects.get(applicant=applicant)
    except ScreeningForm.DoesNotExist:
        screening_form = None

    # Get payment record
    payment = ScreeningPayment.objects.filter(
        applicant=applicant,
        status='success'
    ).first()

    # Get activities and notes
    activities = ApplicationActivity.objects.filter(
        applicant=applicant
    ).select_related('manager')[:20]

    notes = ApplicationNote.objects.filter(
        applicant=applicant
    ).select_related('manager')

    # Handle POST request for status change
    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'change_status':
            new_status = request.POST.get('status')
            comment = request.POST.get('comment', '')

            old_status = applicant.status
            applicant.status = new_status
            applicant.save()

            # Log activity
            ApplicationActivity.objects.create(
                applicant=applicant,
                manager=request.user,
                action='status_changed',
                details=f"Status changed from {old_status} to {new_status}. Comment: {comment}"
            )

            # Send notification to applicant
            if new_status == 'approved':
                notification_message = f"Congratulations! Your application has been approved. You have been offered provisional admission to {applicant.programs.name}."
            elif new_status == 'rejected':
                notification_message = f"We regret to inform you that your application has been unsuccessful. {comment}"
            else:
                notification_message = f"Your application status has been updated to: {applicant.get_status_display()}."

            Notification.objects.create(
                user=applicant.user,
                message=notification_message
            )

            messages.success(request, f'Application status updated to {applicant.get_status_display()}')
            return redirect('accounts:app_manager_applicant_detail', applicant_id=applicant.id)

        elif action == 'add_note':
            note_text = request.POST.get('note')
            if note_text:
                ApplicationNote.objects.create(
                    applicant=applicant,
                    manager=request.user,
                    note=note_text
                )
                ApplicationActivity.objects.create(
                    applicant=applicant,
                    manager=request.user,
                    action='note_added',
                    details=f"Added note: {note_text[:50]}..."
                )
                messages.success(request, 'Note added successfully')
                return redirect('accounts:app_manager_applicant_detail', applicant_id=applicant.id)

        elif action == 'reject_document':
            if screening_form:
                doc_field = request.POST.get('doc_field')
                comment = request.POST.get('comment', '')
                status_field = f'{doc_field}_status'
                comment_field = f'{doc_field}_comment'
                setattr(screening_form, status_field, 'rejected')
                setattr(screening_form, comment_field, comment)
                screening_form.save()

                ApplicationActivity.objects.create(
                    applicant=applicant,
                    manager=request.user,
                    action='document_rejected',
                    details=f"{doc_field.replace('_', ' ').title()} rejected. Reason: {comment}"
                )
                Notification.objects.create(
                    user=applicant.user,
                    message=f"Your {doc_field.replace('_', ' ')} has been rejected. Reason: {comment}. Please re-upload."
                )
                messages.success(request, 'Document rejected and applicant notified.')
                return redirect('accounts:app_manager_applicant_detail', applicant_id=applicant.id)

    context = {
        'applicant': applicant,
        'screening_form': screening_form,
        'payment': payment,
        'activities': activities,
        'notes': notes,
    }

    return render(request, 'app_manager/applicant_detail.html', context)


@ratelimit(key='ip', rate='5/m', method='POST', block=False)
def app_manager_login(request):
    """Login view for application managers"""
    if request.user.is_authenticated and request.user.user_type == 'application_manager':
        return redirect('accounts:app_manager_dashboard')

    if request.method == 'POST':
        if getattr(request, 'limited', False):
            messages.error(request, "Too many login attempts. Please wait a minute and try again.")
            return render(request, 'app_manager/login.html', status=429)

        from django.contrib.auth import authenticate, login

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None and user.user_type == 'application_manager':
            login(request, user)
            return redirect('accounts:app_manager_dashboard')
        else:
            messages.error(request, 'Invalid credentials or insufficient permissions')

    return render(request, 'app_manager/login.html')


@login_required
@user_passes_test(is_application_manager, login_url='/manager/')
def app_manager_documents(request):
    """Document Verification Center"""

    forms = ScreeningForm.objects.select_related(
        'applicant__user', 'applicant__programs'
    ).all()

    # Filter by applicant if passed in query param
    applicant_id = request.GET.get('applicant')
    if applicant_id:
        forms = forms.filter(applicant__id=applicant_id)

    # Filter by document status
    doc_status = request.GET.get('doc_status', 'pending')
    if doc_status == 'pending':
        forms = forms.filter(
            Q(waec_result_status='pending') |
            Q(jamb_result_slip_status='pending') |
            Q(passport_photo_status='pending') |
            Q(birth_certificate_status='pending')
        )
    elif doc_status == 'rejected':
        forms = forms.filter(
            Q(waec_result_status='rejected') |
            Q(jamb_result_slip_status='rejected') |
            Q(passport_photo_status='rejected') |
            Q(birth_certificate_status='rejected')
        )

    # Handle POST (verify/reject individual document)
    if request.method == 'POST':
        form_id = request.POST.get('form_id')
        doc_field = request.POST.get('doc_field')
        action = request.POST.get('action')
        comment = request.POST.get('comment', '')

        try:
            screening = ScreeningForm.objects.get(id=form_id)
            status_field = f'{doc_field}_status'
            comment_field = f'{doc_field}_comment'

            if action == 'verify':
                setattr(screening, status_field, 'verified')
                setattr(screening, comment_field, None)
                activity_action = 'document_verified'
                activity_detail = f"{doc_field.replace('_', ' ').title()} verified"
            elif action == 'reject':
                setattr(screening, status_field, 'rejected')
                setattr(screening, comment_field, comment)
                activity_action = 'document_rejected'
                activity_detail = f"{doc_field.replace('_', ' ').title()} rejected. Reason: {comment}"

                # Notify applicant
                Notification.objects.create(
                    user=screening.applicant.user,
                    message=f"Your {doc_field.replace('_', ' ')} has been rejected. Reason: {comment}. Please re-upload."
                )

            screening.save()

            ApplicationActivity.objects.create(
                applicant=screening.applicant,
                manager=request.user,
                action=activity_action,
                details=activity_detail
            )

            messages.success(request, f'Document {action}d successfully.')
        except ScreeningForm.DoesNotExist:
            messages.error(request, 'Screening form not found.')

        return redirect(request.path + f'?doc_status={doc_status}')

    paginator = Paginator(forms, 20)
    page_obj = paginator.get_page(request.GET.get('page', 1))

    context = {
        'page_obj': page_obj,
        'doc_status': doc_status,
    }
    return render(request, 'app_manager/documents.html', context)


@login_required
@user_passes_test(is_application_manager, login_url='/manager/')
def app_manager_merit_list(request):
    """Merit List Generator"""
    from core.models import Program

    programs = Program.objects.all()
    merit_list = []
    selected_program = None

    if request.GET.get('program'):
        program_id = request.GET.get('program')
        min_score = int(request.GET.get('min_score', 0))
        slots = int(request.GET.get('slots', 100))

        try:
            selected_program = Program.objects.get(id=program_id)

            # Get applicants for this program who have paid and submitted
            applicants = Applicant.objects.filter(
                programs=selected_program,
                screening_payments__status='success'
            ).select_related('user').prefetch_related('screening_forms').distinct()

            # Build merit list with scores
            for applicant in applicants:
                form = applicant.screening_forms.first()
                if form:
                    try:
                        score = int(form.jamb_score) if form.jamb_score else 0
                    except (ValueError, TypeError):
                        score = 0

                    if score >= min_score:
                        merit_list.append({
                            'applicant': applicant,
                            'jamb_score': score,
                            'form': form,
                        })

            # Sort by JAMB score descending
            merit_list.sort(key=lambda x: x['jamb_score'], reverse=True)
            merit_list = merit_list[:slots]

        except Program.DoesNotExist:
            messages.error(request, 'Program not found.')

    # Handle bulk admit action
    if request.method == 'POST' and request.POST.get('action') == 'bulk_admit':
        applicant_ids = request.POST.getlist('applicant_ids')
        admitted_count = 0
        for aid in applicant_ids:
            try:
                app = Applicant.objects.get(id=aid)
                app.status = 'approved'
                app.save()

                Notification.objects.create(
                    user=app.user,
                    message=f"Congratulations! You have been offered provisional admission to {app.programs.name}."
                )

                ApplicationActivity.objects.create(
                    applicant=app,
                    manager=request.user,
                    action='admission_offered',
                    details=f"Admitted via merit list for {app.programs.name}"
                )
                admitted_count += 1
            except Applicant.DoesNotExist:
                pass

        messages.success(request, f'{admitted_count} applicants admitted successfully.')
        return redirect(request.get_full_path())

    context = {
        'programs': programs,
        'merit_list': merit_list,
        'selected_program': selected_program,
        'min_score': request.GET.get('min_score', 0),
        'slots': request.GET.get('slots', 100),
    }
    return render(request, 'app_manager/merit_list.html', context)


@login_required
@user_passes_test(is_application_manager, login_url='/manager/')
def app_manager_communicate(request):
    """Communication Center - Send notifications to applicants"""

    if request.method == 'POST':
        target = request.POST.get('target')
        subject = request.POST.get('subject', '')
        message_text = request.POST.get('message')

        if not message_text:
            messages.error(request, 'Message cannot be empty.')
            return redirect('accounts:app_manager_communicate')

        # Determine recipients
        if target == 'all':
            recipients = Applicant.objects.select_related('user').all()
        elif target == 'admitted':
            recipients = Applicant.objects.filter(status='approved').select_related('user')
        elif target == 'pending':
            recipients = Applicant.objects.filter(status='pending_review').select_related('user')
        elif target == 'rejected':
            recipients = Applicant.objects.filter(status='rejected').select_related('user')
        elif target == 'paid':
            recipients = Applicant.objects.filter(
                screening_payments__status='success'
            ).select_related('user').distinct()
        else:
            recipients = Applicant.objects.none()

        count = 0
        for applicant in recipients:
            personalised = message_text.replace('{name}', applicant.user.get_full_name())
            Notification.objects.create(
                user=applicant.user,
                message=f"{subject}: {personalised}" if subject else personalised
            )
            count += 1

        ApplicationActivity.objects.create(
            applicant=recipients.first() if recipients.exists() else None,
            manager=request.user,
            action='notification_sent',
            details=f"Bulk notification sent to {count} applicants. Target: {target}"
        ) if count > 0 else None

        messages.success(request, f'Notification sent to {count} applicants.')
        return redirect('accounts:app_manager_communicate')

    context = {
        'total_applicants': Applicant.objects.count(),
        'admitted_count': Applicant.objects.filter(status='approved').count(),
        'pending_count': Applicant.objects.filter(status='pending_review').count(),
        'rejected_count': Applicant.objects.filter(status='rejected').count(),
    }
    return render(request, 'app_manager/communicate.html', context)
