# accounts/utils.py

from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required

def student_only(view_func):
    """
    Custom decorator to restrict access to students only.
    """
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        if hasattr(request.user, 'studentprofile'):  # Check if the user has a student profile
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("Access denied. This page is for students only.")
    return _wrapped_view
