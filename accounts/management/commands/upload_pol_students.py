"""
Upload Political Science (POL) Degree students - 100 Level, 2024/2025 session.

Run: python manage.py upload_pol_students
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import (
    Faculty, Department, StudentProfile, Level, AcademicSession,
)

User = get_user_model()

STUDENTS = [
    {"first_name": "Shu'aiba",    "last_name": "Dauda",            "id_number": "LCE/PSC/24U/001", "gender": "M"},
    {"first_name": "Abdulrashid", "last_name": "Usman",            "id_number": "LCE/PSC/24U/002", "gender": "M"},
    {"first_name": "Jolly",       "last_name": "Elisha",           "id_number": "LCE/PSC/24U/003", "gender": "M"},
    {"first_name": "Shamsudeen",  "last_name": "Usman",            "id_number": "LCE/PSC/24U/004", "gender": "M"},
    {"first_name": "Abubakar",    "last_name": "Anis Baragkao",    "id_number": "LCE/PSC/24U/005", "gender": "M"},
    {"first_name": "Mudassir",    "last_name": "Muhammad Otaji",   "id_number": "LCE/PSC/24U/006", "gender": "M"},
    {"first_name": "Bashir",      "last_name": "Sulaiman",         "id_number": "LCE/PSC/24U/007", "gender": "M"},
    {"first_name": "Zakari",      "last_name": "Iliyasu Bello",    "id_number": "LCE/PSC/24U/008", "gender": "M"},
    {"first_name": "Aliyu",       "last_name": "Abdulmumini",      "id_number": "LCE/PSC/24U/009", "gender": "M"},
    {"first_name": "Bello",       "last_name": "Usma",             "id_number": "LCE/PSC/24U/010", "gender": "M"},
    {"first_name": "Abubakar",    "last_name": "Sadiq Abubakar",   "id_number": "LCE/PSC/24U/011", "gender": "M"},
]


class Command(BaseCommand):
    help = "Upload Political Science Degree 100L students for 2024/2025 session (password = ID number)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("\n=== Uploading POL Degree 100L Students ===\n"))

        # Resolve shared objects
        try:
            faculty = Faculty.objects.get(short_name="FOSS", programme_type="degree")
        except Faculty.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                "Faculty 'Faculty of Social Sciences' (FOSS, degree) not found. Run seed_all first."
            ))
            return

        try:
            department = Department.objects.get(short_name="POL", faculty=faculty)
        except Department.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                "Department 'Political Science' (POL) not found in FOSS. Run seed_all first."
            ))
            return

        try:
            level = Level.objects.get(name="100", programme_type="degree")
        except Level.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                "Level '100 Level' (degree) not found. Run seed_all first."
            ))
            return

        try:
            session = AcademicSession.objects.get(name="2024/2025")
        except AcademicSession.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                "Academic session '2024/2025' not found. Run seed_all first."
            ))
            return

        created_count = 0
        skipped_count = 0

        for s in STUDENTS:
            id_number = s["id_number"]
            password = id_number  # password is the ID number

            # Build username from id_number (e.g. lce_psc_24u_001)
            username = id_number.replace("/", "_").lower()
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}_{counter}"
                counter += 1

            # Skip if ID already exists
            if User.objects.filter(id_number=id_number).exists():
                self.stdout.write(self.style.WARNING(
                    f"   SKIP (already exists): {id_number} - {s['first_name']} {s['last_name']}"
                ))
                skipped_count += 1
                continue

            # Create user
            user = User(
                username=username,
                first_name=s["first_name"],
                last_name=s["last_name"],
                user_type="student",
                id_number=id_number,
                is_verified=True,
            )
            user.set_password(password)
            user.save()

            # Update profile (signal may have auto-created it)
            profile, _ = StudentProfile.objects.get_or_create(user=user)
            profile.faculty = faculty
            profile.department = department
            profile.current_level = level
            profile.programme_type = "degree"
            profile.program = "BSc"
            profile.admission_year = "2026"
            profile.gender = s["gender"]
            profile.current_semester = "first"
            profile.current_session = session
            profile.state_of_origin = "Taraba"
            profile.local_government = "Taraba Central"
            profile.save()

            created_count += 1
            self.stdout.write(self.style.SUCCESS(
                f"   Created: {id_number} - {s['first_name']} {s['last_name']}"
            ))

        self.stdout.write(self.style.SUCCESS(
            f"\n=== Done: {created_count} created, {skipped_count} skipped ==="
        ))
        if created_count:
            self.stdout.write(self.style.WARNING(
                "Password for each student = their ID number (e.g. LCE/PSC/24U/001)"
            ))
