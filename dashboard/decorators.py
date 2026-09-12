from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def student_required(view_func):
    """
    Decorator to allow only verified students to access a view.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.user_type == 'student':  # Check if the user is a student
                if request.user.is_verified:  # Check if the user is verified
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(request, "Your account is not verified. Contact the admin.")
                    return redirect('student_login')  # Replace 'login' with your login URL name
            else:
                messages.error(request, "Access denied. Students only.")
                return redirect('student_login')  # Replace 'login' with your login URL name
        else:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('student_login')  # Replace 'login' with your login URL name
    return _wrapped_view


def staff_required(view_func):
    """
    Decorator to allow only verified staff members to access a view.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            if request.user.user_type == 'staff':  # Check if the user is a staff member
                if request.user.is_verified:  # Check if the user is verified
                    return view_func(request, *args, **kwargs)
                else:
                    messages.error(request, "Your account is not verified. Contact the admin.")
                    return redirect('staff_login')
            else:
                messages.error(request, "Access denied. Staff members only.")
                return redirect('staff_login')  # Replace 'login' with your login URL name
        else:
            messages.error(request, "You must be logged in to access this page.")
            return redirect('staff_login')  # Replace 'login' with your login URL name
    return _wrapped_view