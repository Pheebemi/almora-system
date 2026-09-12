from django.core.management.base import BaseCommand
from accounts.models import (
    Faculty, Department, Level, AcademicSession, Course, CourseOffering, User
)

class Command(BaseCommand):
    help = "Upload Mathematics courses for all levels (100-400) with Degree/Diploma separation logic"

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

        # 1. Identify Target Department (Degree Faculty)
        faculty = Faculty.objects.filter(name="Faculty of Science", programme_type="degree").first()
        if not faculty:
            self.stdout.write(self.style.ERROR("Faculty of Science (Degree) not found!"))
            return

        dept = Department.objects.filter(name="Mathematics", faculty=faculty).first()
        if not dept:
            self.stdout.write(self.style.ERROR("Mathematics department (under Faculty of Science) not found!"))
            return

        self.stdout.write(f"Targeting Department: {dept.name} in {faculty.name} ({faculty.programme_type})")

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
                {"code": "GST 111", "title": "Communication in English I", "units": 2, "semester": "first"},
                {"code": "MTH 101", "title": "Elementary Mathematics I", "units": 2, "semester": "first"},
                {"code": "COS 101", "title": "Introduction to Computer Sciences", "units": 3, "semester": "first"},
                {"code": "MTH 103", "title": "Elementary Mathematics III", "units": 2, "semester": "first"},
                {"code": "LCE--MTH 105", "title": "Elementary Polynomial & Matrices.", "units": 2, "semester": "first"},
                {"code": "PHY 101", "title": "General Physics I (Mechanics)", "units": 1, "semester": "first"},
                {"code": "STA 111", "title": "Descriptive Statistics", "units": 3, "semester": "first"},
                # Second Semester
                {"code": "GST 112", "title": "Nigerian Peoples and Culture", "units": 2, "semester": "second"},
                {"code": "GST 122", "title": "Communication in English II", "units": 2, "semester": "second"},
                {"code": "MTH 102", "title": "Elementary Mathematics II", "units": 3, "semester": "second"},
                {"code": "MTH 104", "title": "Linear Algebra", "units": 3, "semester": "second"},
                {"code": "STA 112", "title": "Probability I", "units": 3, "semester": "second"},
                {"code": "PHY 102", "title": "General Physics II", "units": 2, "semester": "second"},
                {"code": "PHY 108", "title": "General Practical Physics", "units": 1, "semester": "second"},
            ],
            "200": [
                # First Semester
                {"code": "ENT 211", "title": "Entrepreneurship and Innovation", "units": 2, "semester": "first"},
                {"code": "COS 201", "title": "Computer Programming I", "units": 3, "semester": "first"},
                {"code": "MTH 201", "title": "Mathematical Methods I", "units": 2, "semester": "first"},
                {"code": "MTH 203", "title": "Sets Logic and Algebra I", "units": 2, "semester": "first"},
                {"code": "MTH 205", "title": "Linear Algebra II", "units": 1, "semester": "first"},
                {"code": "MTH 207", "title": "Real Analysis I", "units": 2, "semester": "first"},
                {"code": "MTH 209", "title": "Introduction to Numerical Analysis", "units": 2, "semester": "first"},
                {"code": "LCE-CSC 205", "title": "Cloud Computing", "units": 2, "semester": "first"},
                # Second Semester
                {"code": "GST 212", "title": "Philosophy, Logic and Human Existence", "units": 2, "semester": "second"},
                {"code": "MTH 202", "title": "Elementary Differential Equations", "units": 2, "semester": "second"},
                {"code": "MTH 204", "title": "Linear Algebra I", "units": 2, "semester": "second"},
                {"code": "MTH 210", "title": "Vector Analysis", "units": 1, "semester": "second"},
                {"code": "LCE-CSC 214", "title": "System Performance Evaluation", "units": 2, "semester": "second"},
                {"code": "LCE-CSC 216", "title": "Data Science I", "units": 2, "semester": "second"},
                {"code": "LCE--MTH 272", "title": "Introduction to Scientific Computing", "units": 3, "semester": "second"},
                {"code": "LCE--MTH 274", "title": "History of Mathematics", "units": 2, "semester": "second"},
            ],
            "300": [
                # First Semester
                {"code": "ENT 311", "title": "Enterprise Appreciation", "units": 2, "semester": "first"},
                {"code": "MTH 301", "title": "Metric Space Topology", "units": 2, "semester": "first"},
                {"code": "MTH 303", "title": "Vector and Tensor Analysis", "units": 2, "semester": "first"},
                {"code": "MTH 305", "title": "Complex Analysis II", "units": 2, "semester": "first"},
                {"code": "MTH 307", "title": "Real Analysis II", "units": 2, "semester": "first"},
                {"code": "MTH 399", "title": "Industrial Attachment II (12 Weeks)", "units": 3, "semester": "first"},
                {"code": "LCE--MTH 335", "title": "Numerical Analysis I", "units": 3, "semester": "first"},
                {"code": "LCE--MTH 319", "title": "Discrete Mathematics", "units": 3, "semester": "first"},
                {"code": "LCE--MTH 319_ALT", "title": "Analytic Dynamics", "units": 2, "semester": "first"},
                {"code": "LCE--MTH 375", "title": "Dynamics of Rigid Body", "units": 2, "semester": "first"},
                {"code": "LCE--MTH 383", "title": "Introduction to Operation Research", "units": 2, "semester": "first"},
                {"code": "LCE--MTH 371", "title": "Differential Geometry", "units": 2, "semester": "first"},
                # Second Semester
                {"code": "GST 312", "title": "Peace and Conflicts Resolutions", "units": 2, "semester": "second"},
                {"code": "MTH 300", "title": "Abstract Algebra I", "units": 2, "semester": "second"},
                {"code": "MTH 302", "title": "Ordinary Differential Equations", "units": 2, "semester": "second"},
                {"code": "MTH 304", "title": "Complex Analysis I", "units": 2, "semester": "second"},
                {"code": "MTH 306", "title": "Abstract Algebra II", "units": 3, "semester": "second"},
                {"code": "MTH 308", "title": "Introduction to Mathematical Modelling", "units": 2, "semester": "second"},
                {"code": "MTH 310", "title": "Mathematical Methods II", "units": 2, "semester": "second"},
            ],
            "400": [
                # First Semester
                {"code": "MTH 401", "title": "Theory of Ordinary Differential Equations", "units": 2, "semester": "first"},
                {"code": "MTH 403", "title": "Functional Analysis", "units": 2, "semester": "first"},
                {"code": "MTH 405", "title": "General Topology", "units": 2, "semester": "first"},
                {"code": "MTH 407", "title": "Mathematical Methods", "units": 2, "semester": "first"},
                {"code": "LCE--MTH 433", "title": "Numerical Analysis II", "units": 2, "semester": "first"},
                {"code": "LCE--MTH 481", "title": "Optimization Theory", "units": 2, "semester": "first"},
                {"code": "LCE--MTH 473", "title": "Analytical Dynamics", "units": 3, "semester": "first"},
                # Second Semester
                {"code": "MTH 402", "title": "Theory Of Partial Differential Equations", "units": 2, "semester": "second"},
                {"code": "MTH 404", "title": "Project", "units": 6, "semester": "second"},
                {"code": "MTH 406", "title": "Lebesgue Measure and Integrals", "units": 2, "semester": "second"},
                {"code": "MTH 408", "title": "Entrepreneurship in Mathematics", "units": 2, "semester": "second"},
                {"code": "LCE--MTH 444", "title": "Mathematical Methods III", "units": 2, "semester": "second"},
                {"code": "LCE--MTH 474", "title": "Fluid Mechanics", "units": 2, "semester": "second"},
                {"code": "LCE--MTH 428", "title": "Systems Theory", "units": 2, "semester": "second"},
                {"code": "LCE--MTH 472", "title": "Field Theory", "units": 2, "semester": "second"},
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
            self.stdout.write(self.style.SUCCESS("\nSuccessfully processed Mathematics curriculum."))
