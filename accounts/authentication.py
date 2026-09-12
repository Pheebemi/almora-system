from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

User = get_user_model()

class StudentIDAuthBackend(BaseBackend):
    """
    Custom authentication backend that allows students to log in 
    using their ID number (e.g., LCE/DIP/CMP/24/0001) and password.
    """
    def authenticate(self, request, username=None, password=None, **kwargs):
        try:
            # Attempt to fetch a user by ID number
            user = User.objects.get(id_number=username)
            if user.check_password(password) and user.user_type == 'student':
                return user
        except User.DoesNotExist:
            return None
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None