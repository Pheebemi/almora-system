from django.contrib import admin
from .models import SupportRequest, Notification
from .forms import ReplySupportForm
from django.shortcuts import render, redirect
from django.urls import path
from django.utils.html import format_html

class SupportRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'subject', 'created_at', 'is_replied', 'user_type')
    list_filter = ('is_replied', 'created_at', 'user__user_type')
    search_fields = ('subject', 'message', 'user__username', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('user', 'subject', 'message', 'created_at')
    date_hierarchy = 'created_at'
    change_form_template = 'admin/support_request_change_form.html'
    
    def user_type(self, obj):
        return obj.user.user_type.title()
    user_type.short_description = 'User Type'

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:support_request_id>/reply/', self.admin_site.admin_view(self.reply_to_support_request), name='reply_to_support_request'),
        ]
        return custom_urls + urls

    def reply_to_support_request(self, request, support_request_id):
        support_request = SupportRequest.objects.get(id=support_request_id)
        if request.method == 'POST':
            form = ReplySupportForm(request.POST)
            if form.is_valid():
                reply = form.cleaned_data['reply']
                support_request.reply = reply
                support_request.is_replied = True
                support_request.save()

                # Create a notification for the user
                Notification.objects.create(
                    user=support_request.user,
                    support_request=support_request,
                    message=f"Your support request '{support_request.subject}' has been replied to."
                )

                self.message_user(request, 'Support request replied successfully.')
                return redirect('admin:dashboard_supportrequest_changelist')
        else:
            form = ReplySupportForm()

        context = {
            'form': form,
            'support_request': support_request,
        }
        return render(request, 'admin/reply_to_support_request.html', context)

    def response_change(self, request, obj):
        if "_reply" in request.POST:
            return redirect('admin:reply_to_support_request', support_request_id=obj.pk)
        return super().response_change(request, obj)

    def has_add_permission(self, request):
        # Only allow viewing and editing, not creating new support requests
        return False

admin.site.register(SupportRequest, SupportRequestAdmin)

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at', 'user__user_type')
    search_fields = ('message', 'user__username', 'user__email')
    readonly_fields = ('user', 'message', 'created_at')
    date_hierarchy = 'created_at'

admin.site.register(Notification, NotificationAdmin)