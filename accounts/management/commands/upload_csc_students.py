"""
Upload Computer Science (CSC) Degree students - 100 Level, 2024/2025 session.

Run: python manage.py upload_csc_students
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import (
    Faculty, Department, StudentProfile, Level, AcademicSession,
)

User = get_user_model()

STUDENTS = [
    {"first_name": "Muhammad",      "last_name": "Yusuf",               "id_number": "LCE/CS/24U/001",  "gender": "M"},
    {"first_name": "Nabila",         "last_name": "A. Shdibu",           "id_number": "LCE/CS/24U/002",  "gender": "F"},
    {"first_name": "Aishetu",        "last_name": "Usman",               "id_number": "LCE/CS/24U/003",  "gender": "F"},
    {"first_name": "Abubakar",       "last_name": "Usman",               "id_number": "LCE/CS/24U/004",  "gender": "M"},
    {"first_name": "Zainab",         "last_name": "A. Muhammadou",       "id_number": "LCE/CS/24U/005",  "gender": "F"},
    {"first_name": "Usman",          "last_name": "Abdulmumini",         "id_number": "LCE/CS/24U/006",  "gender": "M"},
    {"first_name": "Alhasan",        "last_name": "Dr. Sani",            "id_number": "LCE/CS/24U/007",  "gender": "M"},
    {"first_name": "Sani",           "last_name": "Abubakar",            "id_number": "LCE/CS/24U/008",  "gender": "M"},
    {"first_name": "Manjehood",      "last_name": "Ndiyu Zima",          "id_number": "LCE/CS/24U/009",  "gender": "M"},
    {"first_name": "Muhammad",       "last_name": "Tasha Tanka",         "id_number": "LCE/CS/24U/0010", "gender": "M"},
    {"first_name": "Saleh",          "last_name": "A. Bali",             "id_number": "LCE/CS/24U/0011", "gender": "M"},
    {"first_name": "Muhammad",       "last_name": "A. Sulaiman",         "id_number": "LCE/CS/24U/0012", "gender": "M"},
    {"first_name": "Bello",          "last_name": "Mahmud",              "id_number": "LCE/CS/24U/0013", "gender": "M"},
    {"first_name": "Abdulganiyiu",   "last_name": "Y. Idiyero",          "id_number": "LCE/CS/24U/0014", "gender": "M"},
    {"first_name": "Fatima",         "last_name": "M. Bello",            "id_number": "LCE/CS/24U/0015", "gender": "F"},
    {"first_name": "Abdullahi",      "last_name": "A. Usman",            "id_number": "LCE/CS/24U/0016", "gender": "M"},
    {"first_name": "Mansin",         "last_name": "D. Haruna",           "id_number": "LCE/CS/24U/0017", "gender": "M"},
    {"first_name": "Rahinat",        "last_name": "G. Usman",            "id_number": "LCE/CS/24U/0018", "gender": "F"},
    {"first_name": "Ninfiri",        "last_name": "Sheidu",              "id_number": "LCE/CS/24U/0019", "gender": "M"},
    {"first_name": "Mansin",         "last_name": "A. Muhammad",         "id_number": "LCE/CS/24U/0020", "gender": "M"},
    {"first_name": "Khadija",        "last_name": "A. Abdulkadri",       "id_number": "LCE/CS/24U/0021", "gender": "F"},
    {"first_name": "Usman",          "last_name": "Abdullahi",           "id_number": "LCE/CS/24U/0022", "gender": "M"},
    {"first_name": "Hussaini",       "last_name": "A. Muhammad",         "id_number": "LCE/CS/24U/0023", "gender": "M"},
    {"first_name": "Ismail",         "last_name": "A. Damu",             "id_number": "LCE/CS/24U/0024", "gender": "M"},
    {"first_name": "Bala",           "last_name": "Nuhu Markus",         "id_number": "LCE/CS/24U/0025", "gender": "M"},
    {"first_name": "Bola",           "last_name": "Roi",                 "id_number": "LCE/CS/24U/0026", "gender": "M"},
    {"first_name": "Ibadison",       "last_name": "Haruna",              "id_number": "LCE/CS/24U/0027", "gender": "M"},
    {"first_name": "Yusuf",          "last_name": "Genesis",             "id_number": "LCE/CS/24U/0028", "gender": "M"},
]


class Command(BaseCommand):
    help = "Upload Computer Science Degree 100L students for 2024/2025 session (password = ID number)"

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("\n=== Uploading CSC Degree 100L Students ===\n"))

        # Resolve shared objects
        try:
            faculty = Faculty.objects.get(short_name="FOS", programme_type="degree")
        except Faculty.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                "Faculty 'Faculty of Science' (FOS, degree) not found. Run seed_all first."
            ))
            return

        try:
            department = Department.objects.get(short_name="CSC", faculty=faculty)
        except Department.DoesNotExist:
            self.stdout.write(self.style.ERROR(
                "Department 'Computer Science' (CSC) not found in FOS. Run seed_all first."
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

            # Build username from id_number (e.g. lce_cs_24u_001)
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
                "Password for each student = their ID number (e.g. LCE/CS/24U/001)"
            ))
