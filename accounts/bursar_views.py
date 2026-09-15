from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Sum, Q
from django_ratelimit.decorators import ratelimit
from django.views.decorators.csrf import csrf_exempt

from .models import (
    User, BursarProfile, PaymentTransaction, FeeStructure,
    AcademicSession, Department, Level,
)
from .utils import resolve_login_username
from core.models import ScreeningPayment


def is_bursar(user):
    return user.is_authenticated and user.user_type == 'bursar'


@ratelimit(key='ip', rate='5/m', method='POST', block=False)
@csrf_exempt
def bursar_login(request):
    """Login page for bursars"""
    if request.method == 'POST':
        if getattr(request, 'limited', False):
            messages.error(request, "Too many login attempts. Please wait a minute and try again.")
            return render(request, 'accounts/bursar/login.html', status=429)

        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=resolve_login_username(username), password=password)
        if user is not None:
            if user.is_verified:
                if user.user_type == 'bursar':
                    login(request, user)
                    messages.success(request, f"Welcome, {user.get_full_name()}!")
                    return redirect('accounts:bursar_dashboard')
                else:
                    messages.error(request, "Only Bursars are allowed to log in here.")
            else:
                messages.warning(request, 'Your account is not verified. Contact the admin.')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'accounts/bursar/login.html')


def _paid_amount(queryset):
    return queryset.filter(status='success').aggregate(total=Sum('amount'))['total'] or 0


@login_required
@user_passes_test(is_bursar)
def bursar_dashboard(request):
    """Dashboard for bursars: financial overview"""
    current_session = AcademicSession.objects.filter(is_active=True).first()

    school_fees_total = _paid_amount(PaymentTransaction.objects.filter(payment_type='school_fees'))
    acceptance_fees_total = _paid_amount(PaymentTransaction.objects.filter(payment_type='acceptance_fees'))
    other_fees_total = _paid_amount(PaymentTransaction.objects.filter(payment_type='other'))
    application_fees_total = _paid_amount(ScreeningPayment.objects.all())

    total_collected = school_fees_total + acceptance_fees_total + other_fees_total + application_fees_total

    pending_payments = PaymentTransaction.objects.filter(status='pending').count()
    pending_application_fees = ScreeningPayment.objects.filter(status='pending').count()

    recent_payments = PaymentTransaction.objects.filter(
        status='success'
    ).select_related('student__user').order_by('-payment_date')[:10]

    recent_application_fees = ScreeningPayment.objects.filter(
        status='success'
    ).select_related('applicant__user').order_by('-payment_date')[:10]

    context = {
        'bursar': request.user.bursarprofile,
        'current_session': current_session,
        'school_fees_total': school_fees_total,
        'acceptance_fees_total': acceptance_fees_total,
        'other_fees_total': other_fees_total,
        'application_fees_total': application_fees_total,
        'total_collected': total_collected,
        'pending_payments': pending_payments,
        'pending_application_fees': pending_application_fees,
        'recent_payments': recent_payments,
        'recent_application_fees': recent_application_fees,
    }
    return render(request, 'accounts/bursar/dashboard.html', context)


@login_required
@user_passes_test(is_bursar)
def bursar_payments(request):
    """List/filter all student payments (school fees, acceptance fees, other)"""
    payments = PaymentTransaction.objects.select_related('student__user', 'student__department').order_by('-payment_date')

    filter_type = request.GET.get('type', '')
    filter_status = request.GET.get('status', '')
    filter_session = request.GET.get('session', '')
    search_query = request.GET.get('q', '').strip()

    if filter_type:
        payments = payments.filter(payment_type=filter_type)
    if filter_status:
        payments = payments.filter(status=filter_status)
    if filter_session:
        payments = payments.filter(session=filter_session)
    if search_query:
        payments = payments.filter(
            Q(student__user__first_name__icontains=search_query) |
            Q(student__user__last_name__icontains=search_query) |
            Q(student__user__id_number__icontains=search_query) |
            Q(reference__icontains=search_query)
        )

    total_amount = payments.filter(status='success').aggregate(total=Sum('amount'))['total'] or 0

    paginator = Paginator(payments, 25)
    page_obj = paginator.get_page(request.GET.get('page'))

    available_sessions = PaymentTransaction.objects.values_list('session', flat=True).distinct().order_by('-session')

    context = {
        'payments': page_obj,
        'page_obj': page_obj,
        'paginator': paginator,
        'total_amount': total_amount,
        'available_sessions': available_sessions,
        'filter_type': filter_type,
        'filter_status': filter_status,
        'filter_session': filter_session,
        'search_query': search_query,
        'payment_types': PaymentTransaction.PAYMENT_TYPES,
        'payment_statuses': PaymentTransaction.PAYMENT_STATUS,
    }
    return render(request, 'accounts/bursar/payments.html', context)


@login_required
@user_passes_test(is_bursar)
def bursar_application_fees(request):
    """List/filter applicant screening/application fee payments"""
    payments = ScreeningPayment.objects.select_related('applicant__user').order_by('-payment_date')

    filter_status = request.GET.get('status', '')
    search_query = request.GET.get('q', '').strip()

    if filter_status:
        payments = payments.filter(status=filter_status)
    if search_query:
        payments = payments.filter(
            Q(applicant__user__first_name__icontains=search_query) |
            Q(applicant__user__last_name__icontains=search_query) |
            Q(reference__icontains=search_query)
        )

    total_amount = payments.filter(status='success').aggregate(total=Sum('amount'))['total'] or 0

    paginator = Paginator(payments, 25)
    page_obj = paginator.get_page(request.GET.get('page'))

    context = {
        'payments': page_obj,
        'page_obj': page_obj,
        'paginator': paginator,
        'total_amount': total_amount,
        'filter_status': filter_status,
        'search_query': search_query,
    }
    return render(request, 'accounts/bursar/application_fees.html', context)


@login_required
@user_passes_test(is_bursar)
def bursar_fee_structure(request):
    """View and set fee amounts per session/department/level"""
    if request.method == 'POST':
        session_id = request.POST.get('academic_session')
        department_id = request.POST.get('department')
        level_id = request.POST.get('level')
        amount = request.POST.get('amount', '').strip()

        try:
            amount_val = float(amount)
            if amount_val <= 0:
                raise ValueError
        except (ValueError, TypeError):
            messages.error(request, "Enter a valid fee amount.")
            return redirect('accounts:bursar_fee_structure')

        session = get_object_or_404(AcademicSession, id=session_id)
        department = get_object_or_404(Department, id=department_id)
        level = get_object_or_404(Level, id=level_id)

        fee, created = FeeStructure.objects.update_or_create(
            academic_session=session, department=department, level=level,
            defaults={'amount': amount_val}
        )
        if created:
            messages.success(request, f"Fee set for {department.name} - {level.display_name} ({session.name}).")
        else:
            messages.success(request, f"Fee updated for {department.name} - {level.display_name} ({session.name}).")
        return redirect('accounts:bursar_fee_structure')

    fee_structures = FeeStructure.objects.select_related(
        'academic_session', 'department', 'level'
    ).order_by('-academic_session__start_year', 'department__name', 'level__order')

    filter_session = request.GET.get('session', '')
    if filter_session:
        fee_structures = fee_structures.filter(academic_session_id=filter_session)

    context = {
        'fee_structures': fee_structures,
        'available_sessions': AcademicSession.objects.all().order_by('-start_year'),
        'available_departments': Department.objects.select_related('faculty').order_by('faculty__name', 'name'),
        'available_levels': Level.objects.order_by('programme_type', 'order'),
        'filter_session': filter_session,
    }
    return render(request, 'accounts/bursar/fee_structure.html', context)


@login_required
@user_passes_test(is_bursar)
def bursar_delete_fee_structure(request, fee_id):
    """Remove a fee structure entry"""
    fee = get_object_or_404(FeeStructure, id=fee_id)
    if request.method == 'POST':
        label = f"{fee.department.name} - {fee.level.display_name} ({fee.academic_session.name})"
        fee.delete()
        messages.success(request, f"Removed fee for {label}.")
    return redirect('accounts:bursar_fee_structure')
