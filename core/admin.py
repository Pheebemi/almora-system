from django.contrib import admin
from django.shortcuts import render, redirect
from django.contrib import messages as django_messages
from django.utils.html import format_html
from .models import ContactSubmission, Applicant, Program, ProgramChoice, ScreeningForm, AcademicSubject, ExaminationDetail, ScreeningPayment
from dashboard.models import Notification

# Register Program only
admin.site.register([Program])

@admin.register(ProgramChoice)
class ProgramChoiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'program_type', 'is_active', 'created_at')
    list_filter = ('program_type', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    ordering = ('program_type', 'name')
    fields = ('program_type', 'name', 'description', 'is_active')

@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'submitted_at')
    search_fields = ('name', 'email')
    readonly_fields = ('name', 'email', 'message', 'submitted_at')
    list_filter = ('submitted_at',)

class AcademicSubjectInline(admin.TabularInline):
    model = AcademicSubject
    extra = 0
    fields = ('subject', 'grade', 'sitting')

class ExaminationDetailInline(admin.TabularInline):
    model = ExaminationDetail
    extra = 0
    fields = ('sitting', 'exam_type', 'exam_number', 'exam_year')

@admin.register(ExaminationDetail)
class ExaminationDetailAdmin(admin.ModelAdmin):
    list_display = ('screening_form', 'sitting', 'exam_type', 'exam_number', 'exam_year')
    list_filter = ('sitting', 'exam_type', 'exam_year')
    search_fields = ('screening_form__first_name', 'screening_form__surname', 'exam_number')
    ordering = ('screening_form', 'sitting')

@admin.register(AcademicSubject)
class AcademicSubjectAdmin(admin.ModelAdmin):
    list_display = ('screening_form', 'subject', 'grade', 'sitting')
    list_filter = ('sitting', 'subject', 'grade')
    search_fields = ('screening_form__first_name', 'screening_form__surname', 'subject')
    ordering = ('screening_form', 'sitting', 'subject')

@admin.register(ScreeningForm)
class ScreeningFormAdmin(admin.ModelAdmin):
    list_display = (
        'applicant',
        'first_name',
        'surname',
        'jamb_reg_no',
        'jamb_score',
        'state_of_origin',
        'local_government',
        'document_verification_status',
        'academic_subjects_summary',
        'examination_summary',
        'created_at'
    )
    list_filter = (
        'state_of_origin',
        'waec_result_status',
        'jamb_result_slip_status',
        'passport_photo_status',
        'birth_certificate_status',
        'created_at'
    )
    search_fields = (
        'first_name',
        'surname',
        'jamb_reg_no',
        'email',
        'phone_number'
    )
    readonly_fields = (
        'created_at',
        'updated_at',
        'academic_subjects_summary',
        'examination_summary',
        'document_verification_summary_display',
        'waec_result_link',
        'jamb_result_slip_link',
        'passport_photo_link',
        'birth_certificate_link',
    )
    actions = ['verify_all_documents', 'mark_documents_pending']
    
    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('academic_subjects', 'examination_details')
    
    def academic_subjects_summary(self, obj):
        """Display a summary of academic subjects"""
        first_sitting = obj.get_first_sitting_subjects()
        second_sitting = obj.get_second_sitting_subjects()
        
        summary = []
        if first_sitting:
            summary.append(f"First Sitting: {', '.join([f'{s.subject}({s.grade})' for s in first_sitting])}")
        if second_sitting:
            summary.append(f"Second Sitting: {', '.join([f'{s.subject}({s.grade})' for s in second_sitting])}")
        
        return ' | '.join(summary) if summary else 'No subjects added'
    
    def examination_summary(self, obj):
        """Display a summary of examination details"""
        first_exam = obj.get_first_sitting_examination()
        second_exam = obj.get_second_sitting_examination()
        
        summary = []
        if first_exam:
            summary.append(f"First: {first_exam.get_exam_type_display()}({first_exam.exam_year})")
        if second_exam:
            summary.append(f"Second: {second_exam.get_exam_type_display()}({second_exam.exam_year})")
        
        return ' | '.join(summary) if summary else 'No exams added'
    
    academic_subjects_summary.short_description = 'Academic Subjects'
    examination_summary.short_description = 'Examinations'

    def document_verification_status(self, obj):
        """Display document verification status with color badges"""
        summary = obj.get_document_verification_summary()
        if summary['all_verified']:
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">✓ All Verified</span>'
            )
        elif summary['has_rejected']:
            return format_html(
                '<span style="background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">✗ {} Rejected</span>',
                summary['rejected']
            )
        else:
            return format_html(
                '<span style="background-color: #ffc107; color: black; padding: 3px 8px; border-radius: 3px; font-weight: bold;">⏳ {} Pending</span>',
                summary['pending']
            )
    document_verification_status.short_description = 'Document Status'

    def document_verification_summary_display(self, obj):
        """Display detailed document verification summary"""
        summary = obj.get_document_verification_summary()
        return format_html(
            '<div style="padding: 10px; background: #f8f9fa; border-radius: 5px;">'
            '<strong>Verification Summary:</strong><br>'
            '✅ Verified: <strong>{}</strong> | '
            '❌ Rejected: <strong>{}</strong> | '
            '⏳ Pending: <strong>{}</strong> | '
            'Total: <strong>{}</strong>'
            '</div>',
            summary['verified'],
            summary['rejected'],
            summary['pending'],
            summary['total']
        )
    document_verification_summary_display.short_description = 'Verification Summary'

    def waec_result_link(self, obj):
        """Display WAEC result with link and status"""
        if obj.waec_result:
            status_colors = {'pending': '#ffc107', 'verified': '#28a745', 'rejected': '#dc3545'}
            status_color = status_colors.get(obj.waec_result_status, '#6c757d')
            return format_html(
                '<a href="{}" target="_blank" style="margin-right: 10px;">📄 View Document</a>'
                '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
                obj.waec_result.url,
                status_color,
                obj.get_waec_result_status_display()
            )
        return '-'
    waec_result_link.short_description = 'WAEC/NECO Result'

    def jamb_result_slip_link(self, obj):
        """Display JAMB result slip with link and status"""
        if obj.jamb_result_slip:
            status_colors = {'pending': '#ffc107', 'verified': '#28a745', 'rejected': '#dc3545'}
            status_color = status_colors.get(obj.jamb_result_slip_status, '#6c757d')
            return format_html(
                '<a href="{}" target="_blank" style="margin-right: 10px;">📄 View Document</a>'
                '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
                obj.jamb_result_slip.url,
                status_color,
                obj.get_jamb_result_slip_status_display()
            )
        return '-'
    jamb_result_slip_link.short_description = 'JAMB Result Slip'

    def passport_photo_link(self, obj):
        """Display passport photo with link and status"""
        if obj.passport_photo:
            status_colors = {'pending': '#ffc107', 'verified': '#28a745', 'rejected': '#dc3545'}
            status_color = status_colors.get(obj.passport_photo_status, '#6c757d')
            return format_html(
                '<a href="{}" target="_blank" style="margin-right: 10px;">🖼️ View Photo</a>'
                '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
                obj.passport_photo.url,
                status_color,
                obj.get_passport_photo_status_display()
            )
        return '-'
    passport_photo_link.short_description = 'Passport Photo'

    def birth_certificate_link(self, obj):
        """Display birth certificate with link and status"""
        if obj.birth_certificate:
            status_colors = {'pending': '#ffc107', 'verified': '#28a745', 'rejected': '#dc3545'}
            status_color = status_colors.get(obj.birth_certificate_status, '#6c757d')
            return format_html(
                '<a href="{}" target="_blank" style="margin-right: 10px;">📄 View Document</a>'
                '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
                obj.birth_certificate.url,
                status_color,
                obj.get_birth_certificate_status_display()
            )
        return 'Not Uploaded'
    birth_certificate_link.short_description = 'Birth Certificate'

    fieldsets = (
        ('Personal Information', {
            'fields': ('first_name', 'middle_name', 'surname', 'date_of_birth', 'sex', 'state_of_origin', 'local_government', 'email', 'phone_number', 'contact_address')
        }),
        ('JAMB Details', {
            'fields': ('jamb_reg_no', 'jamb_score')
        }),
        ('Academic Information', {
            'fields': ('primary_school', 'primary_school_dates', 'secondary_school', 'secondary_school_dates')
        }),
        ('Program Choices', {
            'fields': ('first_choice', 'second_choice', 'third_choice')
        }),
        ('Document Verification Summary', {
            'fields': ('document_verification_summary_display',),
            'classes': ('wide',)
        }),
        ('Documents & Verification', {
            'fields': (
                'waec_result_link', 'waec_result', 'waec_result_status', 'waec_result_comment',
                'jamb_result_slip_link', 'jamb_result_slip', 'jamb_result_slip_status', 'jamb_result_slip_comment',
                'passport_photo_link', 'passport_photo', 'passport_photo_status', 'passport_photo_comment',
                'birth_certificate_link', 'birth_certificate', 'birth_certificate_status', 'birth_certificate_comment',
                'declaration'
            ),
            'description': 'Click on document links to view. Update status and add comments if rejecting.'
        }),
        ('Verification Metadata', {
            'fields': ('verified_by', 'verified_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    inlines = [AcademicSubjectInline, ExaminationDetailInline]

    def save_model(self, request, obj, form, change):
        """Track who verified documents and send notifications"""
        from django.utils import timezone

        if change:  # If editing existing form
            old_obj = ScreeningForm.objects.get(pk=obj.pk)

            # Check if any verification status changed
            status_changed = False
            rejected_docs = []
            verified_docs = []

            # Check each document's status change
            doc_checks = [
                ('waec_result_status', 'waec_result_comment', 'WAEC/NECO Result'),
                ('jamb_result_slip_status', 'jamb_result_slip_comment', 'JAMB Result Slip'),
                ('passport_photo_status', 'passport_photo_comment', 'Passport Photo'),
                ('birth_certificate_status', 'birth_certificate_comment', 'Birth Certificate'),
            ]

            for status_field, comment_field, doc_name in doc_checks:
                old_status = getattr(old_obj, status_field)
                new_status = getattr(obj, status_field)

                if old_status != new_status:
                    status_changed = True

                    if new_status == 'rejected':
                        comment = getattr(obj, comment_field) or 'No comment provided'
                        rejected_docs.append((doc_name, comment))
                    elif new_status == 'verified':
                        verified_docs.append(doc_name)

            # Update verification metadata if status changed
            if status_changed:
                obj.verified_by = request.user
                obj.verified_at = timezone.now()

                # Send notifications for rejected documents
                if rejected_docs:
                    message_parts = ['The following documents were rejected:']
                    for doc_name, comment in rejected_docs:
                        message_parts.append(f'\n• {doc_name}: {comment}')
                    message_parts.append('\n\nPlease re-upload the correct documents.')

                    Notification.objects.create(
                        user=obj.applicant.user,
                        message=''.join(message_parts)
                    )

                # Send notification if all documents verified
                if obj.all_documents_verified():
                    Notification.objects.create(
                        user=obj.applicant.user,
                        message='All your documents have been verified! Your application is now being processed.'
                    )
                # Or if some verified but not all
                elif verified_docs and not rejected_docs:
                    Notification.objects.create(
                        user=obj.applicant.user,
                        message=f'The following documents have been verified: {", ".join(verified_docs)}'
                    )

        super().save_model(request, obj, form, change)

    def verify_all_documents(self, request, queryset):
        """Bulk action to verify all documents for selected screening forms"""
        from django.utils import timezone

        updated_count = 0
        for screening_form in queryset:
            screening_form.waec_result_status = 'verified'
            screening_form.jamb_result_slip_status = 'verified'
            screening_form.passport_photo_status = 'verified'
            if screening_form.birth_certificate:
                screening_form.birth_certificate_status = 'verified'

            screening_form.verified_by = request.user
            screening_form.verified_at = timezone.now()
            screening_form.save()

            # Send notification
            Notification.objects.create(
                user=screening_form.applicant.user,
                message='All your documents have been verified! Your application is now being processed.'
            )

            updated_count += 1

        django_messages.success(request, f'Successfully verified all documents for {updated_count} screening form(s).')

    verify_all_documents.short_description = "✓ Verify all documents for selected forms"

    def mark_documents_pending(self, request, queryset):
        """Bulk action to mark all documents as pending"""
        updated_count = 0
        for screening_form in queryset:
            screening_form.waec_result_status = 'pending'
            screening_form.jamb_result_slip_status = 'pending'
            screening_form.passport_photo_status = 'pending'
            if screening_form.birth_certificate:
                screening_form.birth_certificate_status = 'pending'
            screening_form.save()
            updated_count += 1

        django_messages.success(request, f'Successfully marked documents as pending for {updated_count} screening form(s).')

    mark_documents_pending.short_description = "⏳ Mark all documents as pending"


@admin.register(ScreeningPayment)
class ScreeningPaymentAdmin(admin.ModelAdmin):
    list_display = ('applicant', 'amount', 'reference', 'status', 'payment_date', 'verified_at')
    list_filter = ('status', 'payment_date', 'verified_at')
    search_fields = ('applicant__user__first_name', 'applicant__user__last_name', 'reference', 'paystack_reference')
    readonly_fields = ('payment_date', 'verified_at')
    ordering = ('-payment_date',)
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('applicant', 'amount', 'reference', 'paystack_reference', 'status')
        }),
        ('Timestamps', {
            'fields': ('payment_date', 'verified_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('applicant__user')

@admin.register(Applicant)
class ApplicantAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'state', 'status')
    list_filter = ('status',)
    list_editable = ('status',)
    search_fields = ('user__username', 'user__email', 'phone_number')
    actions = ['send_notification_to_applicants']

    def send_notification_to_applicants(self, request, queryset):
        """Admin action to send notifications to selected applicants"""
        if request.POST.get('notification_message'):
            # Process the form submission
            message = request.POST.get('notification_message')

            # Create notifications for all selected applicants
            notification_count = 0
            for applicant in queryset:
                Notification.objects.create(
                    user=applicant.user,
                    message=message
                )
                notification_count += 1

            django_messages.success(request, f'Successfully sent notification to {notification_count} applicant(s).')
            return redirect(request.get_full_path())

        # Show the form to enter the notification message
        return render(request, 'admin/send_notification_form.html', {
            'applicants': queryset,
            'action_name': 'send_notification_to_applicants'
        })

    send_notification_to_applicants.short_description = "Send notification to selected applicants"

    def save_model(self, request, obj, form, change):
        """Send notification when applicant status changes"""
        if change:  # If this is an edit (not a new applicant)
            # Get the old status before saving
            try:
                old_status = Applicant.objects.get(pk=obj.pk).status
            except Applicant.DoesNotExist:
                old_status = None

            # Save the model first
            super().save_model(request, obj, form, change)

            # Check if status changed
            if old_status and old_status != obj.status:
                # Create status change notification messages
                status_messages = {
                    'approved': 'Congratulations! Your application has been approved. Check your email for next steps.',
                    'rejected': 'Your application status has been updated. Please contact the admissions office for more information.',
                    'pending_review': 'Your application is now under review. We will notify you once a decision is made.',
                }

                notification_message = status_messages.get(
                    obj.status,
                    f'Your application status has been updated to: {obj.get_status_display()}'
                )

                # Create notification
                Notification.objects.create(
                    user=obj.user,
                    message=notification_message
                )
        else:
            super().save_model(request, obj, form, change)