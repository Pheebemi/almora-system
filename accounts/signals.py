from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from .models import StudentProfile, StaffProfile, ExamOfficerProfile, Faculty, Department, Level
import random
import string
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


def generate_unique_id(prefix, length=10):
    """Generate a unique identifier for matriculation or staff ID."""
    while True:
        random_part = ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))
        full_id = f"{prefix}{random_part}"
        if prefix.startswith('ST'):
            if not User.objects.filter(id_number=full_id).exists():
                return full_id
        elif prefix.startswith('SF'):
            if not StaffProfile.objects.filter(staff_id=full_id).exists():
                return full_id
        elif prefix.startswith('EO'):
            if not ExamOfficerProfile.objects.filter(staff_id=full_id).exists():
                return full_id


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        try:
            if instance.user_type == 'student':
                # Skip if profile already exists (e.g. created by seed script)
                if StudentProfile.objects.filter(user=instance).exists():
                    return

                # ID number is now manually assigned by staff, not auto-generated

                # Assign default faculty and department
                default_faculty = Faculty.objects.first()
                if not default_faculty:
                    default_faculty = Faculty.objects.create(name="Default Faculty", short_name="DF")

                default_department = Department.objects.filter(faculty=default_faculty).first()
                if not default_department:
                    default_department = Department.objects.create(
                        faculty=default_faculty, name="Default Department", short_name="DD"
                    )

                # Get default level (Level instance, not string)
                default_level = Level.objects.filter(name='100').first()
                if not default_level:
                    default_level = Level.objects.first()

                StudentProfile.objects.create(
                    user=instance,
                    date_of_birth=None,
                    gender='',
                    faculty=default_faculty,
                    department=default_department,
                    program='BSc',
                    admission_year='2024',
                    current_level=default_level,
                    permanent_address='',
                    local_government='',
                    state_of_origin='',
                    cgpa=0.00
                )

            elif instance.user_type == 'staff':
                # Skip if profile already exists
                if StaffProfile.objects.filter(user=instance).exists():
                    return

                staff_id = generate_unique_id('SF')

                default_faculty = Faculty.objects.first()
                if not default_faculty:
                    default_faculty = Faculty.objects.create(name="Default Faculty", short_name="DF")

                default_department = Department.objects.filter(faculty=default_faculty).first()
                if not default_department:
                    default_department = Department.objects.create(
                        faculty=default_faculty, name="Default Department", short_name="DD"
                    )

                StaffProfile.objects.create(
                    user=instance,
                    staff_id=staff_id,
                    staff_type='academic',
                    faculty=default_faculty,
                    department=default_department,
                    qualification='',
                    date_employed=None,
                    is_head_of_department=False
                )

            elif instance.user_type == 'exam_officer':
                # Skip if profile already exists
                if ExamOfficerProfile.objects.filter(user=instance).exists():
                    return

                officer_id = generate_unique_id('EO')
                ExamOfficerProfile.objects.create(
                    user=instance,
                    staff_id=officer_id,
                    can_manage_degree=False,
                    can_manage_nd=False,
                    can_manage_nce=False,
                    is_active=True
                )

        except Exception as e:
            logger.error(f"Error creating profile for {instance.username}: {e}")
            raise
