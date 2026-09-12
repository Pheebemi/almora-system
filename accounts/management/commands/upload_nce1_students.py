"""
Upload NCE students - NCE1, 2025/2026 session.

Names for everyone except LCE/NCE/ISS/25/0001 are placeholders ("Student <CODE>")
and are meant to be edited afterwards.

Run: python manage.py upload_nce1_students --dry-run
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
    {"dept": "NCIS", "first_name": "Laurat",  "last_name": "Yakubu",    "id_number": "LCE/NCE/ISS/25/0001",  "gender": "F"},
    {"dept": "NCEN", "first_name": "PLACEHOLDER", "last_name": "PLACEHOLDER", "id_number": "LCE/NCE/ELIS/25/0001", "gender": "M"},
    {"dept": "NCPC", "first_name": "PLACEHOLDER", "last_name": "PLACEHOLDER", "id_number": "LCE/NCE/PSCR/25/0001", "gender": "M"},
    {"dept": "NCSC", "first_name": "PLACEHOLDER", "last_name": "PLACEHOLDER", "id_number": "LCE/NCE/SSCR/25/0001", "gender": "F"},
    {"dept": "NCBE", "first_name": "PLACEHOLDER", "last_name": "PLACEHOLDER", "id_number": "LCE/NCE/BED/25/0001",  "gender": "F"},
]


class Command(BaseCommand):
    help = "Upload NCE1 students for 2025/2026 (password = ID number)"

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

        level = Level.objects.filter(name="NCE1", programme_type="nce").first()
        if not level:
            self.stdout.write(self.style.ERROR("Level 'NCE1' (nce) not found!"))
            return

        session = AcademicSession.objects.filter(name=SESSION_NAME).first()
        if not session:
            self.stdout.write(self.style.ERROR(f"Session '{SESSION_NAME}' not found!"))
            return

        # Mirror the `program` value already used by existing NCE students
        # rather than hardcoding a guess.
        sample = StudentProfile.objects.filter(
            department__faculty__programme_type="nce"
        ).first()
        program = sample.program if sample else "BEd"
        self.stdout.write(f"Using program={program!r} (from existing NCE students)")

        # Resolve every department up front so a bad short_name fails before writes
        depts = {}
        for s in STUDENTS:
            code = s["dept"]
            if code in depts:
                continue
            d = Department.objects.filter(
                short_name=code, faculty__programme_type="nce"
            ).first()
            if not d:
                self.stdout.write(self.style.ERROR(f"Department '{code}' (nce) not found!"))
                return
            depts[code] = d

        created_count = 0
        skipped_count = 0

        with transaction.atomic():
            for s in STUDENTS:
                id_number = s["id_number"]
                department = depts[s["dept"]]

                if User.objects.filter(id_number=id_number).exists():
                    self.stdout.write(self.style.WARNING(
                        f"   SKIP (already exists): {id_number}"
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
                        f"({s['gender']}) -> {username} @ {department.short_name}"
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
                profile.faculty = department.faculty
                profile.department = department
                profile.current_level = level
                profile.programme_type = "nce"
                profile.program = program
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
                "Password for each student = their ID number"
            ))
