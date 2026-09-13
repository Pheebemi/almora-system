# accounts/utils.py

from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required


def resolve_login_username(identifier):
    """
    Login forms accept either a username or an email address. Django's
    auth backend only authenticates by username, so when the submitted
    identifier looks like an email, resolve it to the matching user's
    username first. Falls back to the identifier unchanged if it's not
    an email, or if zero/multiple accounts share that email (ambiguous
    matches are treated as a lookup failure rather than guessing).
    """
    if not identifier or '@' not in identifier:
        return identifier

    from .models import User
    matches = User.objects.filter(email__iexact=identifier)
    if matches.count() == 1:
        return matches.first().username
    return identifier

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
