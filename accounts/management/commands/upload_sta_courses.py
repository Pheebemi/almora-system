from django.core.management.base import BaseCommand
from accounts.models import (
    Faculty, Department, Level, AcademicSession, Course, CourseOffering, User
)

class Command(BaseCommand):
    help = "Upload Statistics courses for all levels (100-400) with Degree/Diploma separation logic"

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

        # Ensure Statistics department exists or find existing one
        dept, d_created = Department.objects.get_or_create(
            name="Statistics",
            faculty=faculty,
            defaults={"short_name": "STA"}
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
        # Note: Handled duplicates by using _ALT or _SEM2 suffixes
        courses_by_level = {
            "100": [
                # First Semester
                {"code": "GST 111", "title": "Communication in English", "units": 2, "semester": "first"},
                {"code": "COS 101", "title": "Introduction to Computer Science", "units": 3, "semester": "first"},
                {"code": "MTH 101", "title": "Elementary Mathematics I", "units": 2, "semester": "first"},
                {"code": "STA 111", "title": "Descriptive Statistics", "units": 3, "semester": "first"},
                # Second Semester
                {"code": "GST 112", "title": "Nigerian Peoples and Culture", "units": 2, "semester": "second"},
                {"code": "MTH 102", "title": "Elementary Mathematics II", "units": 2, "semester": "second"},
                {"code": "STA 112", "title": "Probability I", "units": 3, "semester": "second"},
                {"code": "STA 121", "title": "Statistical Inference I", "units": 3, "semester": "second"},
                {"code": "STA 122", "title": "Statistical Computing I", "units": 3, "semester": "second"},
            ],
            "200": [
                # First Semester
                {"code": "ENT 211", "title": "Entrepreneurship and Innovation", "units": 2, "semester": "first"},
                {"code": "STA 211", "title": "Probability II", "units": 3, "semester": "first"},
                {"code": "STA 221", "title": "Statistical Inference II", "units": 3, "semester": "first"},
                {"code": "STA 231", "title": "Statistical Computing II", "units": 2, "semester": "first"},
                {"code": "STA 299", "title": "Industrial Attachment I (12 Weeks)", "units": 3, "semester": "first"},
                # Second Semester
                {"code": "GST 212", "title": "Philosophy, Logic, and Human Existence", "units": 2, "semester": "second"},
                {"code": "STA 202", "title": "Statistics for Physical Sciences & Engineering", "units": 3, "semester": "second"},
                {"code": "STA 212", "title": "Introduction to Social & Economic Statistics", "units": 3, "semester": "second"},
                {"code": "LCE--STA 222", "title": "Biometrics I", "units": 3, "semester": "second"},
            ],
            "300": [
                # First Semester
                {"code": "STA 311", "title": "Probability III", "units": 3, "semester": "first"},
                {"code": "STA 321", "title": "Statistical Inference III", "units": 3, "semester": "first"},
                {"code": "STA 399", "title": "Industrial Attachment II (12 Weeks)", "units": 3, "semester": "first"},
                {"code": "LCE--STA339", "title": "Demography", "units": 3, "semester": "first"},
                {"code": "LCE-STA 347", "title": "Design & Analysis of Experiment I", "units": 3, "semester": "first"},
                # Second Semester
                {"code": "GST 312", "title": "Peace and Conflict Resolution", "units": 2, "semester": "second"},
                {"code": "ENT 312", "title": "Venture Creation", "units": 2, "semester": "second"},
                {"code": "STA 312", "title": "Distribution theory I", "units": 3, "semester": "second"},
                {"code": "STA 322", "title": "Regression and Analysis of Variance I", "units": 2, "semester": "second"},
                {"code": "STA 324", "title": "Survey methods and sampling theory", "units": 3, "semester": "second"},
                {"code": "LCE--STA347", "title": "Design & Analysis of Experiments I", "units": 3, "semester": "second"},
            ],
            "400": [
                # First Semester
                {"code": "STA 411", "title": "Probability IV", "units": 3, "semester": "first"},
                {"code": "STA 413", "title": "Statistical Inference IV", "units": 3, "semester": "first"},
                {"code": "STA 415", "title": "Regression and Analysis of Variance II", "units": 3, "semester": "first"},
                {"code": "STA 499_SEM1", "title": "Research Project", "units": 3, "semester": "first"},
                {"code": "LCE--STA 421", "title": "Design & Analysis of Experiments II", "units": 3, "semester": "first"},
                {"code": "LCE--STA 423", "title": "Multivariate Analysis", "units": 3, "semester": "first"},
                {"code": "LCE--STA 417", "title": "Time Series Analysis", "units": 2, "semester": "first"},
                {"code": "LCE--STA477", "title": "Medical Statistics", "units": 2, "semester": "first"},
                {"code": "LCE--STA407", "title": "Energy Statistics", "units": 2, "semester": "first"},
                # Second Semester
                {"code": "STA 412", "title": "Distribution Theory II", "units": 3, "semester": "second"},
                {"code": "STA 422", "title": "Logical Background of Statistics & Decision Theory", "units": 3, "semester": "second"},
                {"code": "STA 499_SEM2", "title": "Research Project", "units": 3, "semester": "second"},
                {"code": "LCE--STA424", "title": "Nonparametric Methods", "units": 3, "semester": "second"},
                {"code": "LCE--STA 426", "title": "Stochastic Process", "units": 3, "semester": "second"},
                {"code": "LCE--STA 432", "title": "Statistical Quality Control", "units": 3, "semester": "second"},
                {"code": "LCE--STA 428", "title": "Operations Research", "units": 2, "semester": "second"},
                {"code": "LCE--STA458", "title": "Econometric Methods", "units": 2, "semester": "second"},
                {"code": "LCE--STA430", "title": "Biometric Methods II", "units": 2, "semester": "second"},
                {"code": "LCE--STA428_ALT", "title": "Bayesian Inference", "units": 2, "semester": "second"},
                {"code": "LCE--STA476", "title": "Environmental Statistics", "units": 2, "semester": "second"},
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
                # For our internal ALT/SEM2 codes, don't safety-check them (they are fresh)
                if "_ALT" in original_code or "_SEM" in original_code:
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
            self.stdout.write(self.style.SUCCESS("\nSuccessfully processed Statistics curriculum."))
