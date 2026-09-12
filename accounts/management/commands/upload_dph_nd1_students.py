"""
Upload Public Health (DPH) ND students - ND1, 2025/2026 session.

Run: python manage.py upload_dph_nd1_students --dry-run
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

from accounts.models import (
    Department, StudentProfile, Level, AcademicSession,
)

User = get_user_model()

SESSION_NAME = "2025/2026"
ADMISSION_YEAR = "2025"

STUDENTS = [
    {"first_name": "Khadija",  "last_name": "Nuhu",             "id_number": "LCE/DIP/PH/25/0001", "gender": "F"},
    {"first_name": "Josline",  "last_name": "Zachariah Sunkani", "id_number": "LCE/DIP/PH/25/0002", "gender": "M"},
    {"first_name": "Auta",     "last_name": "Doseng",           "id_number": "LCE/DIP/PH/25/0003", "gender": "M"},
    {"first_name": "Liatu",    "last_name": "Josephh",          "id_number": "LCE/DIP/PH/25/0004", "gender": "M"},
    {"first_name": "Naja'atu", "last_name": "Suleiaman",        "id_number": "LCE/DIP/PH/25/0005", "gender": "F"},
    {"first_name": "Aisha",    "last_name": "Suleiman",         "id_number": "LCE/DIP/PH/25/0006", "gender": "F"},
    {"first_name": "Eli",      "last_name": "Johnson",          "id_number": "LCE/DIP/PH/25/0007", "gender": "M"},
    {"first_name": "Yussi",    "last_name": "William",          "id_number": "LCE/DIP/PH/25/0008", "gender": "M"},
    {"first_name": "Samiya",   "last_name": "Usman",            "id_number": "LCE/DIP/PH/25/0009", "gender": "F"},
    {"first_name": "Maryam",   "last_name": "Adam Ba",          "id_number": "LCE/DIP/PH/25/0010", "gender": "F"},
    {"first_name": "Azima",    "last_name": "M. Abubakar",      "id_number": "LCE/DIP/PH/25/0011", "gender": "F"},
    {"first_name": "Elijah",   "last_name": "Martin King",      "id_number": "LCE/DIP/PH/25/0012", "gender": "M"},
    {"first_name": "Munira",   "last_name": "Mohammed Tuwa",    "id_number": "LCE/DIP/PH/25/0013", "gender": "F"},
    {"first_name": "Aisha",    "last_name": "Ibrahim Ya'u",     "id_number": "LCE/DIP/PH/25/0014", "gender": "F"},
    {"first_name": "Zainab",   "last_name": "Aminu",            "id_number": "LCE/DIP/PH/25/0015", "gender": "F"},
    {"first_name": "Hanifa",   "last_name": "Sani",             "id_number": "LCE/DIP/PH/25/0016", "gender": "F"},
    {"first_name": "Sakina",   "last_name": "Buba Mahmud",      "id_number": "LCE/DIP/PH/25/0017", "gender": "F"},
    {"first_name": "Afinike",  "last_name": "August",           "id_number": "LCE/DIP/PH/25/0018", "gender": "F"},
    {"first_name": "Mansura",  "last_name": "Mohamme Tuwa",     "id_number": "LCE/DIP/PH/25/0019", "gender": "F"},
    {"first_name": "Umar",     "last_name": "Yahaya",           "id_number": "LCE/DIP/PH/25/0020", "gender": "M"},
    {"first_name": "Faisal",   "last_name": "Hamza Lanko",      "id_number": "LCE/DIP/PH/25/0021", "gender": "M"},
    {"first_name": "Muhammed", "last_name": "Umar",             "id_number": "LCE/DIP/PH/25/0022", "gender": "M"},
    {"first_name": "Nathan",   "last_name": "Ali",              "id_number": "LCE/DIP/PH/25/0023", "gender": "M"},
    {"first_name": "Khadija",  "last_name": "Shehu Shagari",    "id_number": "LCE/DIP/PH/25/0024", "gender": "F"},
    {"first_name": "Dauda",    "last_name": "Mohammed",         "id_number": "LCE/DIP/PH/25/0025", "gender": "M"},
    {"first_name": "Sokew",    "last_name": "Sagir Yahaya",     "id_number": "LCE/DIP/PH/25/0026", "gender": "M"},
    {"first_name": "Isma'il",  "last_name": "Rabi'u",           "id_number": "LCE/DIP/PH/25/0027", "gender": "M"},
    {"first_name": "Umar",     "last_name": "Muazu",            "id_number": "LCE/DIP/PH/25/0028", "gender": "M"},
    {"first_name": "Mus'ab",   "last_name": "Habu Bala",        "id_number": "LCE/DIP/PH/25/0029", "gender": "M"},
    {"first_name": "Shamsiya", "last_name": "Al Mustapha",      "id_number": "LCE/DIP/PH/25/0030", "gender": "F"},
    {"first_name": "Amina",    "last_name": "Usman",            "id_number": "LCE/DIP/PH/25/0031", "gender": "M"},
]


class Command(BaseCommand):
    help = "Upload Public Health ND1 students for 2025/2026 (password = ID number)"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run without saving changes to the database',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be saved."))

        # Department resolved by short_name within the ND stream so faculty
        # naming differences between environments don't break the lookup.
        department = Department.objects.filter(
            short_name="DPH", faculty__programme_type="nd"
        ).first()
        if not department:
            self.stdout.write(self.style.ERROR("Department 'DPH' (nd) not found!"))
            return
        faculty = department.faculty
        self.stdout.write(f"Department: {department.name} | Faculty: {faculty.name}")

        level = Level.objects.filter(name="ND1", programme_type="nd").first()
        if not level:
            self.stdout.write(self.style.ERROR("Level 'ND1' (nd) not found!"))
            return

        session = AcademicSession.objects.filter(name=SESSION_NAME).first()
        if not session:
            self.stdout.write(self.style.ERROR(f"Session '{SESSION_NAME}' not found!"))
            return

        created_count = 0
        skipped_count = 0

        with transaction.atomic():
            for s in STUDENTS:
                id_number = s["id_number"]

                if User.objects.filter(id_number=id_number).exists():
                    self.stdout.write(self.style.WARNING(
                        f"   SKIP (already exists): {id_number} - {s['first_name']} {s['last_name']}"
                    ))
                    skipped_count += 1
                    continue

                username = id_number.replace("/", "_").lower()
                base_username = username
                counter = 1
                while User.objects.filter(username=username).exists():
                    username = f"{base_username}_{counter}"
                    counter += 1

                if dry_run:
                    self.stdout.write(
                        f"   [DRY-RUN] {id_number} - {s['first_name']} {s['last_name']} "
                        f"({s['gender']}) -> {username}"
                    )
                    created_count += 1
                    continue

                user = User(
                    username=username,
                    first_name=s["first_name"],
                    last_name=s["last_name"],
                    user_type="student",
                    id_number=id_number,
                    is_verified=True,
                )
                user.set_password(id_number)  # password = ID number
                user.save()

                profile, _ = StudentProfile.objects.get_or_create(user=user)
                profile.faculty = faculty
                profile.department = department
                profile.current_level = level
                profile.programme_type = "nd"
                profile.program = "BSc"
                profile.admission_year = ADMISSION_YEAR
                profile.gender = s["gender"]
                profile.current_semester = "first"
                profile.current_session = session
                profile.state_of_origin = ""
                profile.local_government = ""
                profile.save()

                created_count += 1
                self.stdout.write(self.style.SUCCESS(
                    f"   Created: {id_number} - {s['first_name']} {s['last_name']}"
                ))

            if dry_run:
                transaction.set_rollback(True)

        self.stdout.write(self.style.SUCCESS(
            f"\n=== {created_count} to create, {skipped_count} skipped ==="
        ))
        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run - nothing written."))
        else:
            self.stdout.write(self.style.WARNING(
                "Password for each student = their ID number (e.g. LCE/DIP/PH/25/0001)"
            ))
