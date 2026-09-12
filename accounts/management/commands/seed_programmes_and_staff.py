"""
Seed faculties and departments for Degree, ND, and NCE programmes,
and create sample staff users under each.
Run: python manage.py seed_programmes_and_staff
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import (
    Faculty,
    Department,
    StaffProfile,
    Level,
)

User = get_user_model()

# Default password for seeded staff (change after first login)
DEFAULT_STAFF_PASSWORD = "staff123"

DATA = {
    "degree": {
        "faculty": {"name": "Faculty of Science", "short_name": "FOS"},
        "departments": [
            {"name": "Computer Science", "short_name": "CSC"},
            {"name": "Mathematics", "short_name": "MTH"},
            {"name": "Physics", "short_name": "PHY"},
        ],
        "staff": [
            {"username": "degree_staff1", "first_name": "John", "last_name": "Okoro"},
            {"username": "degree_staff2", "first_name": "Amina", "last_name": "Bello"},
        ],
    },
    "nd": {
        "faculty": {"name": "School of ND (Diploma) Studies", "short_name": "NDS"},
        "departments": [
            {"name": "ND Computer Science", "short_name": "ND-CSC"},
            {"name": "ND Engineering", "short_name": "ND-ENG"},
        ],
        "staff": [
            {"username": "nd_staff1", "first_name": "Ibrahim", "last_name": "Yusuf"},
            {"username": "nd_staff2", "first_name": "Fatima", "last_name": "Hassan"},
        ],
    },
    "nce": {
        "faculty": {"name": "School of NCE Education", "short_name": "NCE"},
        "departments": [
            {"name": "NCE Primary Education", "short_name": "NCE-PED"},
            {"name": "NCE Arts Education", "short_name": "NCE-ART"},
        ],
        "staff": [
            {"username": "nce_staff1", "first_name": "Grace", "last_name": "Eze"},
            {"username": "nce_staff2", "first_name": "Chidi", "last_name": "Nwosu"},
        ],
    },
}


class Command(BaseCommand):
    help = "Seed faculties, departments for Degree/ND/NCE and create staff under them"

    def add_arguments(self, parser):
        parser.add_argument(
            "--password",
            type=str,
            default=DEFAULT_STAFF_PASSWORD,
            help="Password for created staff users (default: staff123)",
        )

    def handle(self, *args, **options):
        password = options["password"]
        created_faculties = 0
        created_departments = 0
        created_staff = 0

        for programme_type, config in DATA.items():
            # Faculty (match on programme_type + short_name so we don't mix streams)
            faculty, fac_created = Faculty.objects.get_or_create(
                programme_type=programme_type,
                short_name=config["faculty"]["short_name"],
                defaults={"name": config["faculty"]["name"]},
            )
            if fac_created:
                created_faculties += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Created faculty: {faculty.name} ({programme_type})'
                    )
                )
            else:
                self.stdout.write(f'Faculty already exists: {faculty.name} ({programme_type})')

            # Departments
            for dept_data in config["departments"]:
                dept, dept_created = Department.objects.get_or_create(
                    faculty=faculty,
                    short_name=dept_data["short_name"],
                    defaults={"name": dept_data["name"]},
                )
                if dept_created:
                    created_departments += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  Created department: {dept.name} under {faculty.name}'
                        )
                    )

            # First department for assigning staff
            first_dept = Department.objects.filter(faculty=faculty).first()
            if not first_dept:
                self.stdout.write(
                    self.style.WARNING(
                        f'  No department under {faculty.name}, skipping staff'
                    )
                )
                continue

            # Staff users
            for staff_data in config["staff"]:
                username = staff_data["username"]
                user, user_created = User.objects.get_or_create(
                    username=username,
                    defaults={
                        "user_type": "staff",
                        "is_verified": True,
                        "is_staff": True,
                        "first_name": staff_data["first_name"],
                        "last_name": staff_data["last_name"],
                        "email": f"{username}@almorapoly.edu.ng",
                    },
                )
                if user_created:
                    user.set_password(password)
                    user.save()
                    # Signal creates StaffProfile with first faculty/dept; update to this programme
                    profile, _ = StaffProfile.objects.get_or_create(
                        user=user,
                        defaults={
                            "staff_id": f"SF-{username.upper()}",
                            "staff_type": "academic",
                            "faculty": faculty,
                            "department": first_dept,
                            "qualification": "B.Sc",
                        },
                    )
                    if profile.faculty_id != faculty.id or profile.department_id != first_dept.id:
                        profile.faculty = faculty
                        profile.department = first_dept
                        profile.qualification = profile.qualification or "B.Sc"
                        profile.save()
                    created_staff += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  Created staff: {username} ({user.get_full_name()}) -> {faculty.name} / {first_dept.name}'
                        )
                    )
                else:
                    # Update existing staff profile to this faculty/dept if not set
                    try:
                        profile = user.staffprofile
                        if profile.faculty_id != faculty.id or profile.department_id != first_dept.id:
                            profile.faculty = faculty
                            profile.department = first_dept
                            profile.save()
                            self.stdout.write(
                                f'  Updated staff: {username} -> {faculty.name} / {first_dept.name}'
                            )
                    except StaffProfile.DoesNotExist:
                        pass

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. Created: {created_faculties} faculties, {created_departments} departments, {created_staff} staff."
            )
        )
        if created_faculties + created_departments + created_staff == 0:
            self.stdout.write(
                self.style.NOTICE(
                    "All data already exists (run is idempotent). Summary below."
                )
            )
        if created_staff > 0:
            self.stdout.write(
                self.style.WARNING(
                    f"Staff default password: {password} (change after first login)."
                )
            )
        self.stdout.write("\n--- Programmes summary ---")
        for pt in ("degree", "nd", "nce"):
            facs = Faculty.objects.filter(programme_type=pt).order_by("name")
            for f in facs:
                depts = list(Department.objects.filter(faculty=f).values_list("name", flat=True))
                staff = list(
                    StaffProfile.objects.filter(faculty=f).values_list("user__username", flat=True)
                )
                self.stdout.write(f"  {f.name} ({pt}): depts={depts}, staff={staff}")
