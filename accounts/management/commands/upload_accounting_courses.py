from django.core.management.base import BaseCommand
from accounts.models import (
    Faculty, Department, Level, AcademicSession, Course, CourseOffering, User
)

class Command(BaseCommand):
    help = "Upload 400 Level Accounting courses for First and Second Semesters"

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

        # 1. Ensure Faculty and Department exist
        faculty, f_created = Faculty.objects.get_or_create(
            short_name="FOMS",
            programme_type="degree",
            defaults={"name": "Faculty of Management Sciences"}
        )
        if f_created:
            self.stdout.write(f"Created Faculty: {faculty.name}")

        dept, d_created = Department.objects.get_or_create(
            faculty=faculty,
            short_name="ACC",
            defaults={"name": "Accounting"}
        )
        if d_created:
            self.stdout.write(f"Created Department: {dept.name}")

        # 2. Get Session
        session = AcademicSession.objects.filter(is_active=True).first()
        if not session:
            self.stdout.write(self.style.ERROR("No active Academic Session found!"))
            return

        admin_user = User.objects.filter(is_superuser=True).first()

        # 3. Define Course Data with Levels (Only 400 Level now)
        courses_by_level = {
            "400": [
                # First Semester
                {"code": "ACS 401", "title": "Further Life Contingencies", "units": 3, "semester": "first"},
                {"code": "ACS 403", "title": "Mortality Analysis", "units": 3, "semester": "first"},
                {"code": "ACS 405", "title": "Advanced Risk Management", "units": 3, "semester": "first"},
                {"code": "ACC 499", "title": "Project", "units": 3, "semester": "first"},
                {"code": "LCE--ACC407", "title": "Digital Accounting", "units": 2, "semester": "first"},
                {"code": "LCE--ACC409", "title": "Sustainability and Green Accounting", "units": 2, "semester": "first"},
                {"code": "LCE--ACC411", "title": "Human Resource Accounting", "units": 2, "semester": "first"},
                # Second Semester
                {"code": "ACS 402", "title": "Pension funds and Social Insurance", "units": 3, "semester": "second"},
                {"code": "ACS 404", "title": "Actuarial Valuation", "units": 3, "semester": "second"},
                {"code": "ACC 490", "title": "Project", "units": 3, "semester": "second"},
                {"code": "LCE--ACC408", "title": "Mineral Resource Accounting", "units": 2, "semester": "second"},
                {"code": "LCE--ACC412", "title": "Forensic Accounting & Fraud Examination", "units": 2, "semester": "second"},
            ]
        }

        # 4. Process Courses by Level
        for level_name, courses in courses_by_level.items():
            level = Level.objects.filter(name=level_name).first()
            if not level:
                self.stdout.write(self.style.ERROR(f"Level '{level_name}' not found! Skipping..."))
                continue

            self.stdout.write(self.style.MIGRATE_HEADING(f"\nProcessing Courses for Level: {level.display_name}"))

            for c in courses:
                course_code = c["code"]
                course_title = c["title"]
                units = c["units"]
                semester = c["semester"]

                if dry_run:
                    self.stdout.write(f"[DRY-RUN] Processing {course_code}: {course_title} ({units} Units, {semester})")
                    continue

                # Create or Update Course
                course, created = Course.objects.update_or_create(
                    code=course_code,
                    defaults={
                        "title": course_title,
                        "credits": units,
                        "semester": semester,
                        "academic_session": session,
                        "created_by": admin_user
                    }
                )
                
                action = "Created" if created else "Updated"
                self.stdout.write(f"{action} Course: {course.code}")

                # Create Course Offering
                offering, o_created = CourseOffering.objects.get_or_create(
                    course=course,
                    department=dept,
                    level=level,
                    defaults={"is_active": True}
                )
                if o_created:
                    self.stdout.write(f"   Linked {course.code} to {dept.name} @ {level.display_name}")
                else:
                    self.stdout.write(f"   Offering already exists for {course.code} in {dept.name}")

        if not dry_run:
            self.stdout.write(self.style.SUCCESS("\nSuccessfully processed all Accounting courses."))
