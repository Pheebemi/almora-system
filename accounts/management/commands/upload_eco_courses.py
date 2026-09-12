from django.core.management.base import BaseCommand
from accounts.models import (
    Faculty, Department, Level, AcademicSession, Course, CourseOffering, User
)

class Command(BaseCommand):
    help = "Upload Economics courses for all levels (100-400) with Degree/Diploma separation logic"

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

        # 1. Identify Target Faculty & Department
        faculty = Faculty.objects.filter(name="Faculty of Social Sciences", programme_type="degree").first()
        if not faculty:
            self.stdout.write(self.style.ERROR("Faculty of Social Sciences (Degree) not found!"))
            return

        dept, d_created = Department.objects.get_or_create(
            name="Economics",
            faculty=faculty,
            defaults={"short_name": "ECO"}
        )
        if d_created:
            self.stdout.write(f"Created Department: {dept.name}")
        else:
            self.stdout.write(f"Using existing Department: {dept.name}")

        # 2. Get active Session
        session = AcademicSession.objects.filter(is_active=True).first()
        if not session:
            self.stdout.write(self.style.ERROR("No active Academic Session found!"))
            return

        admin_user = User.objects.filter(is_superuser=True).first()

        # 3. Define Course Data
        courses_by_level = {
            "100": [
                # First Semester
                {"code": "GST 111", "title": "Communication Skills in English", "units": 2, "semester": "first"},
                {"code": "ECO 101", "title": "Principles of Economics I", "units": 3, "semester": "first"},
                {"code": "ECO 103", "title": "Introductory Mathematics I", "units": 3, "semester": "first"},
                {"code": "ECO 105", "title": "Introductory Statistics for Economics I", "units": 3, "semester": "first"},
                {"code": "BUS 101", "title": "Introduction to Management I", "units": 2, "semester": "first"},
                {"code": "ACC 101_ECO", "title": "Introduction to Economics I", "units": 2, "semester": "first"},
                {"code": "LCE-ECO 107", "title": "Structure Of North East Economy I", "units": 2, "semester": "first"},
                {"code": "SOC 101", "title": "Introduction to Sociology I", "units": 2, "semester": "first", "is_elective": True},
                {"code": "POL 101", "title": "Introduction to Political Science I", "units": 2, "semester": "first", "is_elective": True},
                {"code": "PUB 101", "title": "Introduction to Public Administration I", "units": 2, "semester": "first", "is_elective": True},
                # Second Semester
                {"code": "GST 112", "title": "Nigerian Peoples and Culture", "units": 2, "semester": "second"},
                {"code": "ECO 102", "title": "Principles of Economics II", "units": 3, "semester": "second"},
                {"code": "ECO 104", "title": "Introductory Mathematics II", "units": 3, "semester": "second"},
                {"code": "BUS 102", "title": "Introduction to Management II", "units": 2, "semester": "second"},
                {"code": "ECO 106", "title": "Introductory Statistics for Economics II", "units": 3, "semester": "second"},
                {"code": "ACC 102_ECO", "title": "Introduction to Economics II", "units": 3, "semester": "second"},
                {"code": "LCE-ECO 108", "title": "Structure Of North East Economy II", "units": 2, "semester": "second"},
                {"code": "SOC 102", "title": "Introduction to Anthropology", "units": 2, "semester": "second", "is_elective": True},
                {"code": "POL 102", "title": "Introduction to African Politics", "units": 2, "semester": "second", "is_elective": True},
                {"code": "PUB 102", "title": "Introduction to Public Administration II", "units": 2, "semester": "second", "is_elective": True},
            ],
            "200": [
                # First Semester
                {"code": "ECO 207", "title": "Mathematics for Economists", "units": 2, "semester": "first"},
                {"code": "ECO 205", "title": "Structure of the Nigerian Economy I", "units": 2, "semester": "first"},
                {"code": "ENT 211", "title": "Entrepreneurship and Innovation", "units": 2, "semester": "first"},
                {"code": "ECO 201", "title": "Introduction to Micro Economic I", "units": 3, "semester": "first"},
                {"code": "ECO 203", "title": "Introduction Macro Economic I", "units": 3, "semester": "first"},
                {"code": "LCE-ECO 215", "title": "Environmental Economics I", "units": 2, "semester": "first"},
                {"code": "ECO 209", "title": "Economics of Human Resources", "units": 2, "semester": "first", "is_elective": True},
                {"code": "ECO 213", "title": "Financial System", "units": 2, "semester": "first", "is_elective": True},
                # Second Semester
                {"code": "GST 212", "title": "Philosophy, Logic and Human Existence", "units": 2, "semester": "second"},
                {"code": "SSC 202", "title": "Introduction to Computer and its Application", "units": 3, "semester": "second"},
                {"code": "ECO 202", "title": "Introduction to Microeconomics II", "units": 2, "semester": "second"},
                {"code": "ECO 204", "title": "Introduction Macro Economic II", "units": 2, "semester": "second"},
                {"code": "ECO 206", "title": "Intermediate Statistics", "units": 2, "semester": "second"},
                {"code": "ECO 208", "title": "Mathematics for Economist II", "units": 2, "semester": "second"},
                {"code": "ECO 210", "title": "Structure of Nigerian Economic II", "units": 2, "semester": "second"},
                {"code": "ECO 212", "title": "Principle of Finance", "units": 2, "semester": "second"},
                {"code": "LCE-ECO 214", "title": "Environmental Economics II", "units": 2, "semester": "second"},
                {"code": "LCE-ECO 216", "title": "Transport Economics", "units": 2, "semester": "second"},
            ],
            "300": [
                # First Semester
                {"code": "ECO 301", "title": "Intermediate Microeconomics I", "units": 2, "semester": "first"},
                {"code": "ECO 303", "title": "Intermediate Macroeconomics I", "units": 2, "semester": "first"},
                {"code": "ECO 305", "title": "History of Economic Thought", "units": 2, "semester": "first"},
                {"code": "ECO 307", "title": "Project Evaluation", "units": 3, "semester": "first"},
                {"code": "SSC 301", "title": "Innovation in the Social Sciences", "units": 2, "semester": "first"},
                {"code": "ECO 309", "title": "Economics of Development I", "units": 2, "semester": "first"},
                {"code": "ECO 315", "title": "Public Policy", "units": 2, "semester": "first"},
                {"code": "LCE-ECO 317", "title": "Agricultural Economics", "units": 2, "semester": "first"},
                {"code": "LCE-ECO 319", "title": "Food Economics I", "units": 2, "semester": "first"},
                {"code": "ECO 311", "title": "International Economics I", "units": 2, "semester": "first", "is_elective": True},
                {"code": "ECO 313", "title": "Operational Research", "units": 2, "semester": "first", "is_elective": True},
                # Second Semester
                {"code": "GST 312", "title": "Peace and Conflict Resolution", "units": 2, "semester": "second"},
                {"code": "ENT 312", "title": "Venture Creation", "units": 2, "semester": "second"},
                {"code": "ECO 302", "title": "Intermediate Microeconomics II", "units": 2, "semester": "second"},
                {"code": "ECO 304", "title": "Intermediate Macroeconomics II", "units": 2, "semester": "second"},
                {"code": "ECO 306", "title": "Introductory Econometrics", "units": 3, "semester": "second"},
                {"code": "ECO 308", "title": "Public Sector Economics", "units": 2, "semester": "second"},
                {"code": "ECO 310", "title": "Economics of Development II", "units": 2, "semester": "second"},
                {"code": "SSC 302", "title": "Research Method I", "units": 2, "semester": "second"},
                {"code": "LCE-ECO 314", "title": "Agricultural Economics II", "units": 2, "semester": "second"},
                {"code": "LCE-ECO 316", "title": "Food Economics II", "units": 2, "semester": "second"},
                {"code": "ECO 312", "title": "International Economics II", "units": 2, "semester": "second", "is_elective": True},
                {"code": "ECO 318", "title": "Industrial Economics", "units": 2, "semester": "second", "is_elective": True},
            ],
            "400": [
                # First Semester
                {"code": "ECO 401", "title": "Advanced Microeconomics I", "units": 2, "semester": "first"},
                {"code": "ECO 403", "title": "Advanced Macroeconomics I", "units": 2, "semester": "first"},
                {"code": "ECO 405", "title": "Economic Planning", "units": 3, "semester": "first"},
                {"code": "ECO 407", "title": "Fiscal Policy and Analysis", "units": 3, "semester": "first"},
                {"code": "ECO 499", "title": "Research Project/Original Essay", "units": 3, "semester": "first"},
                {"code": "SSC 401", "title": "Research Method II", "units": 2, "semester": "first"},
                {"code": "LCE-ECO 409", "title": "Information Economics I", "units": 2, "semester": "first"},
                {"code": "LCE-ECO 411", "title": "Health Economics", "units": 2, "semester": "first"},
                # Second Semester
                {"code": "ECO 402", "title": "Advanced Microeconomics II", "units": 2, "semester": "second"},
                {"code": "ECO 404", "title": "Advanced Macroeconomics II", "units": 2, "semester": "second"},
                {"code": "ECO 406", "title": "Monetary Theory and Policy", "units": 3, "semester": "second"},
                {"code": "ECO 414", "title": "Economics of Production", "units": 3, "semester": "second"},
                {"code": "ECO 416", "title": "Comparative Economics System", "units": 2, "semester": "second"},
                {"code": "LCE-ECO 410", "title": "Information Economics II", "units": 3, "semester": "second"},
                {"code": "LCE-ECO 412", "title": "Health Economics II", "units": 3, "semester": "second"},
            ]
        }

        # 4. Helper to resolve cross-programme code collisions
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
                new_code = f"{original_code}_DEG"
                self.stdout.write(self.style.WARNING(f"Collision: '{original_code}' exists in a different programme. Using '{new_code}' for Degree."))
                return new_code
            
            return original_code

        # 5. Process Levels
        for level_name, courses in courses_by_level.items():
            level = Level.objects.filter(name=level_name).first()
            if not level:
                self.stdout.write(self.style.ERROR(f"Level '{level_name}' not found!"))
                continue

            self.stdout.write(self.style.MIGRATE_HEADING(f"\n--- Level: {level.display_name} ---"))

            for c in courses:
                original_code = c["code"]
                # Handle our special link codes for repeated courses or ALTs
                if "_ECO" in original_code:
                    real_code = original_code.replace("_ECO", "")
                    safe_code = get_safe_code(real_code, faculty.programme_type)
                    # Force suffix if title/units clash even within same programme
                    if safe_code == real_code:
                        safe_code = original_code
                else:
                    safe_code = get_safe_code(original_code, faculty.programme_type)
                
                if dry_run:
                    self.stdout.write(f"[DRY-RUN] Process {safe_code}: {c['title']} ({c['units']} Units)")
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
                    self.stdout.write(f"   Offering already exists for {course.code} in {dept.name}")

        if not dry_run:
            self.stdout.write(self.style.SUCCESS("\nSuccessfully processed Economics curriculum."))
