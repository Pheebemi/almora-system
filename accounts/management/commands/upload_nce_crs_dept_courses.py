from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import (
    Faculty, Department, Level, AcademicSession, Course, CourseOffering, User
)

# The three CRS courses are new to prod, so they carry full data.
# Everything else already exists and is linked without being edited.
CRS_COURSES = [
    {"code": "CRS 111", "title": "Introduction to the Old Testament", "units": 2, "semester": "first"},
    {"code": "CRS 112", "title": "History of Christianity I", "units": 2, "semester": "first"},
    {"code": "CRS 113", "title": "Philosophy of Religion", "units": 2, "semester": "first"},
]

# Shared education/general courses carried by every NCE department (first semester).
SHARED = [
    {"code": "EDU 111", "link_only": True},
    {"code": "EDU 112", "link_only": True},
    {"code": "EDU 113", "link_only": True},
    {"code": "GSE111", "link_only": True},
]

DEPARTMENTS = {
    "NCPC": {
        "name": "NCE Political Science and Christian Religious Studies",
        "NCE1": SHARED + [
            # Mirrors NCPS minus the English (ENG1xx) half.
            # GST111 overlaps GSE111 on prod; kept deliberately to match NCPS.
            {"code": "GST111", "link_only": True},
            {"code": "POL 111", "link_only": True},
            {"code": "POL 112", "link_only": True},
            {"code": "POL 113", "link_only": True},
            {"code": "POL 114", "link_only": True},
        ] + CRS_COURSES,
    },
    "NCSC": {
        "name": "NCE Social Studies and Christian Religious Studies",
        "NCE1": SHARED + [
            # Mirrors NCIS minus the Islamic Studies (ISS1xx) half
            {"code": "SOS 111", "link_only": True},
            {"code": "SOS 112", "link_only": True},
            {"code": "SOS 113", "link_only": True},
        ] + CRS_COURSES,
    },
}


class Command(BaseCommand):
    help = "Upload NCE 1 first-semester courses for the two new CRS departments"

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Run the script without saving changes to the database',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be saved."))

        faculty = Faculty.objects.filter(
            name="NCE Education", programme_type="nce"
        ).first()
        if not faculty:
            self.stdout.write(self.style.ERROR("NCE Education (NCE) not found!"))
            return

        session = AcademicSession.objects.filter(is_active=True).first()
        if not session:
            self.stdout.write(self.style.ERROR("No active Academic Session found!"))
            return
        self.stdout.write(f"Active session: {session.name}")

        admin_user = User.objects.filter(is_superuser=True).first()

        with transaction.atomic():
            for short_name, config in DEPARTMENTS.items():
                dept = Department.objects.filter(
                    faculty=faculty, short_name=short_name
                ).first()
                if not dept:
                    self.stdout.write(self.style.ERROR(
                        f"Department '{short_name}' not found - skipped"
                    ))
                    continue

                self.stdout.write(self.style.NOTICE(
                    f"\n=== {dept.name} ({dept.short_name}) ==="
                ))

                for level_name, courses in config.items():
                    if level_name == "name":
                        continue

                    level = Level.objects.filter(
                        name=level_name, programme_type="nce"
                    ).first()
                    if not level:
                        self.stdout.write(self.style.ERROR(f"Level '{level_name}' not found!"))
                        continue

                    self.stdout.write(f"--- Level: {level.display_name} ---")

                    for c in courses:
                        code = c["code"]

                        if c.get("link_only"):
                            course = Course.objects.filter(code=code).first()
                            if not course:
                                self.stdout.write(self.style.ERROR(
                                    f"  {code} marked link_only but does not exist - skipped"
                                ))
                                continue
                            if dry_run:
                                self.stdout.write(
                                    f"  [DRY-RUN] {course.code}: {course.title[:40]} "
                                    f"({course.credits}u) -> link existing, no edit"
                                )
                                continue
                        else:
                            if dry_run:
                                exists = Course.objects.filter(code=code).first()
                                state = "reuse existing" if exists else "create new course"
                                self.stdout.write(
                                    f"  [DRY-RUN] {code}: {c['title']} "
                                    f"({c['units']}u) -> {state}"
                                )
                                continue

                            course, created = Course.objects.update_or_create(
                                code=code,
                                defaults={
                                    "title": c["title"],
                                    "credits": c["units"],
                                    "semester": c["semester"],
                                    "academic_session": session,
                                    "created_by": admin_user,
                                    "is_active": True,
                                }
                            )
                            self.stdout.write(
                                f"  {'Created' if created else 'Updated'} Course: {course.code}"
                            )

                        offering, o_created = CourseOffering.objects.get_or_create(
                            course=course,
                            department=dept,
                            level=level,
                            defaults={"is_active": True}
                        )
                        if o_created:
                            self.stdout.write(f"     Linked {course.code} @ {level.display_name}")
                        else:
                            self.stdout.write(f"     Offering already exists for {course.code}")

            if dry_run:
                transaction.set_rollback(True)

        if dry_run:
            self.stdout.write(self.style.WARNING(
                "\nDry run - nothing was written. Re-run without --dry-run to apply."
            ))
        else:
            self.stdout.write(self.style.SUCCESS("\nDone."))
