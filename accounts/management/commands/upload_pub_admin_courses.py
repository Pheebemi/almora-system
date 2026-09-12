from django.core.management.base import BaseCommand
from accounts.models import (
    Faculty, Department, Level, AcademicSession, Course, CourseOffering, User
)

class Command(BaseCommand):
    help = "Upload Public Administration courses for all levels (100-400)"

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
            short_name="PAD",
            defaults={"name": "Public Administration"}
        )
        if d_created:
            self.stdout.write(f"Created Department: {dept.name}")

        # 2. Get Session
        session = AcademicSession.objects.filter(is_active=True).first()
        if not session:
            self.stdout.write(self.style.ERROR("No active Academic Session found!"))
            return

        admin_user = User.objects.filter(is_superuser=True).first()

        # 3. Define Course Data with Levels
        courses_by_level = {
            "100": [
                # First Semester
                {"code": "AMS101C", "title": "Principles of Management", "units": 2, "semester": "first"},
                {"code": "AMS 103C", "title": "Introduction to Computer", "units": 2, "semester": "first"},
                {"code": "PAD 101C", "title": "Introduction to Public Administration", "units": 3, "semester": "first"},
                {"code": "PAD 103C", "title": "Traditional Administrative System", "units": 3, "semester": "first"},
                {"code": "LCE-PAD 105F", "title": "Introduction to Sociology", "units": 3, "semester": "first"},
                {"code": "LCE-PAD 107F", "title": "Introduction to Accounting for Public Administration I", "units": 3, "semester": "first"},
                {"code": "LCE-PAD 109F", "title": "Introduction to Economic for Public Administration I", "units": 3, "semester": "first"},
                {"code": "GST 101C", "title": "Communication in English I", "units": 2, "semester": "first"},
                # Second Semester
                {"code": "AMS102C", "title": "Basic Mathematics", "units": 2, "semester": "second"},
                {"code": "AMS 104C", "title": "Principle of Project Management", "units": 2, "semester": "second"},
                {"code": "PAD 102F", "title": "Elements of Government", "units": 2, "semester": "second"},
                {"code": "LCE-PAD 106F", "title": "Individuals, Group & Society", "units": 2, "semester": "second"},
                {"code": "LCE-PAD 108F", "title": "Introduction to psychology", "units": 2, "semester": "second"},
                {"code": "LCE-PAD 110", "title": "Introduction to Accounting for Public Administration II", "units": 3, "semester": "second"},
                {"code": "LCE-PAD 112", "title": "Introduction to Economics II", "units": 3, "semester": "second"},
                {"code": "GST112C", "title": "Nigerian People and Culture", "units": 2, "semester": "second"},
            ],
            "200": [
                # First Semester
                {"code": "LCE-PAD 201", "title": "Elements of Public Administration", "units": 3, "semester": "first"},
                {"code": "LCE-PAD 203", "title": "Introduction to Political Science", "units": 3, "semester": "first"},
                {"code": "PAD 205", "title": "Office Administration", "units": 2, "semester": "first"},
                {"code": "LCE-PAD 207", "title": "Des. Statistics for Public Administration I", "units": 2, "semester": "first"},
                {"code": "LCE-PAD 209", "title": "Introduction to Micro Economics", "units": 2, "semester": "first"},
                {"code": "LCE-PAD 211", "title": "Public Sector Accounting I", "units": 2, "semester": "first"},
                {"code": "LCE-PAD 213", "title": "Elements of Business Administration", "units": 2, "semester": "first"},
                {"code": "ENT211", "title": "Entrepreneurship and Innovation", "units": 2, "semester": "first"},
                # Second Semester
                {"code": "PAD 202", "title": "Nigerian Government & Administration", "units": 3, "semester": "second"},
                {"code": "LCE-PAD 204", "title": "Public Administration in Nigeria", "units": 3, "semester": "second"},
                {"code": "LCE-PAD 206", "title": "Social Psychology", "units": 2, "semester": "second"},
                {"code": "LCE-PAD 208", "title": "Inferential Statistic for Public Administration", "units": 2, "semester": "second"},
                {"code": "LCE-PAD 210", "title": "Introduction to Macroeconomics", "units": 2, "semester": "second"},
                {"code": "LCE-PAD 212", "title": "Public Sector Accounting II", "units": 2, "semester": "second"},
                {"code": "LCE-PAD 215", "title": "Rural & Community Development", "units": 2, "semester": "second"},
                {"code": "PAD 214", "title": "E-governance in Nigeria", "units": 2, "semester": "second"},
                {"code": "LCE-PAD 216", "title": "Gender Mainstreaming in Development", "units": 2, "semester": "second"},
                {"code": "GST212_PAD", "code_original": "GST212", "title": "Philosophy, Logic & Human Existence", "units": 2, "semester": "second"},
            ],
            "300": [
                # First Semester
                {"code": "PAD 301", "title": "Administrative Theory", "units": 3, "semester": "first"},
                {"code": "LCE-PAD 303", "title": "Nigerian Economy I", "units": 3, "semester": "first"},
                {"code": "PAD 305", "title": "Public Personnel Management", "units": 3, "semester": "first"},
                {"code": "PAD 307", "title": "Research Methodology", "units": 3, "semester": "first"},
                {"code": "PAD 309", "title": "Administrative Law", "units": 3, "semester": "first"},
                {"code": "PAD 311", "title": "Inter-Government Relation", "units": 2, "semester": "first"},
                {"code": "GST 301", "title": "Introduction to Entrepreneurship Studies", "units": 2, "semester": "first"},
                # Second Semester
                {"code": "LCE-PAD 302", "title": "Administrative Behavior", "units": 3, "semester": "second"},
                {"code": "LCE-PAD 304", "title": "Nigerian Economy II", "units": 3, "semester": "second"},
                {"code": "PAD 306", "title": "Development Administration", "units": 3, "semester": "second"},
                {"code": "PAD308", "title": "Local Government Administration in Nigeria", "units": 3, "semester": "second"},
                {"code": "PAD310", "title": "International Relations", "units": 2, "semester": "second"},
                {"code": "LCE-PAD312", "title": "Manpower Planning and Development", "units": 2, "semester": "second"},
                {"code": "LCE-PAD314", "title": "Conflict Management", "units": 2, "semester": "second"},
                {"code": "GST 302", "title": "Introduction to Entrepreneurship Skills", "units": 2, "semester": "second"},
            ],
            "400": [
                # First Semester
                {"code": "PUB 471", "title": "Theory and Practice of Planning", "units": 3, "semester": "first"},
                {"code": "PUB 473", "title": "Public Policy Making and Analysis", "units": 3, "semester": "first"},
                {"code": "PUB 475", "title": "Workshop in Public Administration I", "units": 3, "semester": "first"},
                {"code": "PUB 477", "title": "Public Financial Management", "units": 3, "semester": "first"},
                {"code": "LCE-PUB 479", "title": "Cost Management Accounting", "units": 3, "semester": "first"},
                {"code": "LCE-PUB 481", "title": "Issues in Development", "units": 3, "semester": "first"},
                {"code": "PUB 483", "title": "Social and Welfare Administration in Nigeria", "units": 2, "semester": "first"},
                {"code": "PUB 485", "title": "Rural and Community Development", "units": 2, "semester": "first"},
                # Second Semester
                {"code": "PUB 472", "title": "Project Analysis & Management", "units": 3, "semester": "second"},
                {"code": "PUB 474", "title": "Comparative Public Administration", "units": 3, "semester": "second"},
                {"code": "PUB 476", "title": "Workshop in Public Administration II", "units": 3, "semester": "second"},
                {"code": "PUB 478", "title": "Research Project", "units": 6, "semester": "second"},
                {"code": "PUB 480", "title": "Public Enterprises Management", "units": 2, "semester": "second"},
                {"code": "LCE-PUB 482", "title": "Sustainable Development", "units": 2, "semester": "second"},
                {"code": "LCE-PUB 484", "title": "Urban & Regional Planning", "units": 2, "semester": "second"},
                {"code": "LCE-PUB 486", "title": "Civil Society Organization", "units": 2, "semester": "second"},
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
            self.stdout.write(self.style.SUCCESS("\nSuccessfully processed all Public Administration courses."))
