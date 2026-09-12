from django.core.management.base import BaseCommand
from accounts.models import (
    Faculty, Department, Level, AcademicSession, Course, CourseOffering, User
)

class Command(BaseCommand):
    help = "Upload NCE Business Education courses for all levels (NCE 1 - NCE 2)"

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

        # 1. Faculty & Department (NCE stream)
        faculty = Faculty.objects.filter(
            name="NCE Education", programme_type="nce"
        ).first()
        if not faculty:
            self.stdout.write(self.style.ERROR("NCE Education (NCE) not found!"))
            return

        dept = Department.objects.filter(name="NCE Business Education", faculty=faculty).first()
        if dept:
            self.stdout.write(f"Using existing Department: {dept.name} ({dept.short_name})")
        elif dry_run:
            self.stdout.write("[DRY-RUN] Would create Department: NCE Business Education (NCE-BUS)")
        else:
            dept = Department.objects.create(
                name="NCE Business Education",
                faculty=faculty,
                short_name="NCE-BUS",
            )
            self.stdout.write(f"Created Department: {dept.name}")

        # 2. Get active Session
        session = AcademicSession.objects.filter(is_active=True).first()
        if not session:
            self.stdout.write(self.style.ERROR("No active Academic Session found!"))
            return

        admin_user = User.objects.filter(is_superuser=True).first()

        # 3. Define Course Data
        courses_by_level = {
            "NCE1": [
                # First Semester
                {"code": "BED 110", "title": "Introduction to Vocational Education", "units": 2, "semester": "first"},
                {"code": "BED 112", "title": "Business Mathematics", "units": 2, "semester": "first"},
                {"code": "BED 114", "title": "Introduction to Economics", "units": 2, "semester": "first"},
                {"code": "BED 115", "title": "Office Practice I", "units": 2, "semester": "first"},
                {"code": "BED 116", "title": "Computer Keyboarding", "units": 2, "semester": "first"},
                {"code": "BED 117", "title": "Introduction to Entrepreneurship", "units": 2, "semester": "first"},
                {"code": "GSE 011", "title": "Media and Information Literacy", "units": 1, "semester": "first"},
                {"code": "GSE 113", "title": "Basic General Mathematics I", "units": 1, "semester": "first"},
                # Existing shared NCE courses - link an offering only, leave the
                # course record untouched so we don't clobber the other departments.
                {"code": "EDU 111", "link_only": True},
                {"code": "EDU 112", "link_only": True},
                {"code": "EDU 113", "link_only": True},
                # EDU 101 is deliberately excluded - it is a degree-stream course
                # (Biology/Health/Maths Education); NCE students take the EDU 111-113 set.
            ],
            "NCE2": [],
        }

        # 4. Helper to resolve cross-programme code collisions.
        #    Suffix follows the programme being uploaded, so an NCE course never
        #    inherits a _DEG code from the degree stream (and vice versa).
        SUFFIX = {"degree": "_DEG", "nd": "_ND", "nce": "_NCE"}

        def get_safe_code(original_code, target_programme):
            existing = Course.objects.filter(code=original_code).first()
            if not existing:
                return original_code

            # Check if existing course is already linked to a different programme
            is_cross_programme = False
            for offering in existing.offerings.all():
                if offering.department.faculty.programme_type != target_programme:
                    is_cross_programme = True
                    break

            if is_cross_programme:
                return f"{original_code}{SUFFIX[target_programme]}"

            return original_code

        # 5. Process Levels
        for level_name, courses in courses_by_level.items():
            level = Level.objects.filter(name=level_name, programme_type="nce").first()
            if not level:
                self.stdout.write(self.style.ERROR(f"Level '{level_name}' not found!"))
                continue

            self.stdout.write(self.style.NOTICE(f"\n--- Level: {level.display_name} ---"))

            for c in courses:
                original_code = c["code"]

                # Link-only: the course already exists and is owned by other
                # departments. Attach an offering without editing the course.
                if c.get("link_only"):
                    course = Course.objects.filter(code=original_code).first()
                    if not course:
                        self.stdout.write(self.style.ERROR(
                            f"{original_code} marked link_only but does not exist - skipped"
                        ))
                        continue
                    if dry_run:
                        self.stdout.write(
                            f"[DRY-RUN] {course.code}: {course.title} "
                            f"({course.credits} Units) -> link existing course, no edit"
                        )
                        continue
                    self.stdout.write(f"Reusing Course: {course.code} - {course.title}")
                else:
                    safe_code = get_safe_code(original_code, faculty.programme_type)

                    if dry_run:
                        exists = Course.objects.filter(code=safe_code).first()
                        state = "reuse existing course" if exists else "create new course"
                        renamed = f" (renamed from {original_code})" if safe_code != original_code else ""
                        self.stdout.write(
                            f"[DRY-RUN] {safe_code}: {c['title']} ({c['units']} Units) -> {state}{renamed}"
                        )
                        continue

                    # I. Course Record
                    course, created = Course.objects.update_or_create(
                        code=safe_code,
                        defaults={
                            "title": c["title"],
                            "credits": c["units"],
                            "semester": c["semester"],
                            "academic_session": session,
                            "created_by": admin_user,
                            "is_active": True
                        }
                    )
                    action = "Created" if created else "Updated"
                    self.stdout.write(f"{action} Course: {course.code}")

                # II. Course Offering (The Link)
                offering, o_created = CourseOffering.objects.get_or_create(
                    course=course,
                    department=dept,
                    level=level,
                    defaults={"is_active": True}
                )
                if o_created:
                    self.stdout.write(f"   Linked {course.code} to {dept.name} @ {level.display_name}")
                else:
                    self.stdout.write(f"   Offering already exists for {course.code}")

        if not dry_run:
            self.stdout.write(self.style.SUCCESS("\nSuccessfully processed NCE Business Education curriculum."))
