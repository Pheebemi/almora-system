from django.core.management.base import BaseCommand
from accounts.models import (
    Faculty, Department, Level, AcademicSession, Course, CourseOffering, User
)

class Command(BaseCommand):
    help = "Upload Sociology courses for all levels (100-400) with Degree/Diploma separation logic"

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

        # 1. Identify/Create Target Faculty & Department
        faculty, f_created = Faculty.objects.get_or_create(
            name="Faculty of Social Sciences",
            programme_type="degree"
        )
        if f_created:
            self.stdout.write(f"Created Faculty: {faculty.name}")

        dept, d_created = Department.objects.get_or_create(
            name="Sociology",
            faculty=faculty,
            defaults={"short_name": "SOC"}
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
        # Note: Handled SOC 302/305 appearing in both semesters by linking them to both
        courses_by_level = {
            "100": [
                # First Semester
                {"code": "GST 111", "title": "Communication Skills in English", "units": 2, "semester": "first"},
                {"code": "SOC 101", "title": "Introduction to Sociology I", "units": 2, "semester": "first"},
                {"code": "SOC 103", "title": "Introduction to African Societies & Culture", "units": 2, "semester": "first"},
                {"code": "SOC 105", "title": "Elements of Scientific Thought", "units": 4, "semester": "first"},
                {"code": "LCE-SOC 107", "title": "The Jukun and their Neighbors", "units": 2, "semester": "first"},
                {"code": "LCE-SOC 109", "title": "Introduction to Civic and Social Values", "units": 3, "semester": "first"},
                # Second Semester
                {"code": "GST 112", "title": "Nigerian Peoples and Culture", "units": 2, "semester": "second"},
                {"code": "SOC 102", "title": "Introduction to Anthropology", "units": 2, "semester": "second"},
                {"code": "SOC 104", "title": "Introduction to Psychology", "units": 2, "semester": "second"},
                {"code": "SOC 106", "title": "Introduction to Sociology II", "units": 2, "semester": "second"},
                {"code": "ENG 112", "title": "English Language II", "units": 3, "semester": "second"},
                {"code": "LCE-SOC 103", "title": "Use of Library and study skills", "units": 2, "semester": "second", "is_elective": True},
                {"code": "LCE-SOC 104", "title": "Entrepreneurship Studies", "units": 2, "semester": "second", "is_elective": True},
            ],
            "200": [
                # First Semester
                {"code": "ENT 211", "title": "Entrepreneurship and Innovation", "units": 2, "semester": "first"},
                {"code": "SOC 201", "title": "History of Social Thought", "units": 3, "semester": "first"},
                {"code": "SOC 205", "title": "Elements of Social Work", "units": 2, "semester": "first"},
                {"code": "SOC 203", "title": "Sociology of the Family", "units": 2, "semester": "first"},
                {"code": "SOC 209", "title": "Language in Society & Culture", "units": 2, "semester": "first"},
                {"code": "LCE-SOC 209", "title": "Insecurity in North-Eastern Nigeria", "units": 2, "semester": "first"},
                {"code": "LCE-SOC 211", "title": "Academic Writing for Social Sciences", "units": 2, "semester": "first"},
                # Second Semester
                {"code": "GST 212", "title": "Philosophy, Logic and Human Existence", "units": 2, "semester": "second"},
                {"code": "SSC 202", "title": "Introduction to Computer and its Application", "units": 3, "semester": "second"},
                {"code": "PSY 204", "title": "Introduction to Social Psychology", "units": 2, "semester": "second"},
                {"code": "SOC 210", "title": "Gender and Society", "units": 2, "semester": "second"},
                {"code": "SOC 202", "title": "Social Change and Social Problems", "units": 3, "semester": "second"},
                {"code": "SOC 206", "title": "Structure of the Nigerian Society", "units": 2, "semester": "second"},
                {"code": "LCE-SOC 108", "title": "Nigerian Heritage", "units": 2, "semester": "second"},
                {"code": "LCE-SOC 110", "title": "Descriptive Statistics in Sociology", "units": 2, "semester": "second"},
                {"code": "LCE-SOC 112", "title": "Individual, Group and Society", "units": 1, "semester": "second", "is_elective": True},
                {"code": "LCE-SOC 114", "title": "Learning Processes", "units": 2, "semester": "second", "is_elective": True},
            ],
            "300": [
                # First Semester
                {"code": "SSC301", "title": "Innovation in the Social Sciences", "units": 2, "semester": "first"},
                {"code": "SOC301", "title": "Methods of Social Research & Statistics", "units": 4, "semester": "first"},
                {"code": "SOC 302", "title": "Social Inequality", "units": 2, "semester": "first"},
                {"code": "SOC 305", "title": "Political Sociology", "units": 2, "semester": "first"},
                {"code": "LCE-SOC 307", "title": "Organizational Behavior", "units": 1, "semester": "first"},
                # Second Semester
                {"code": "GST 312", "title": "Peace and Conflict Resolution", "units": 2, "semester": "second"},
                {"code": "ENT 312", "title": "Venture Creation", "units": 2, "semester": "second"},
                {"code": "SSC 302", "title": "Research Method I", "units": 2, "semester": "second"},
                {"code": "SOC 302_LINK_SEM2", "title": "Social Inequality", "units": 2, "semester": "second"},
                {"code": "SOC 305_LINK_SEM2", "title": "Political Sociology", "units": 2, "semester": "second"},
                {"code": "SOC 306", "title": "Formal Organizations", "units": 2, "semester": "second"},
                {"code": "LCE-SOC 306", "title": "Group Dynamics and Intergroup Relations", "units": 2, "semester": "second"},
                {"code": "LCE-SOC 308", "title": "Rural Sociology", "units": 2, "semester": "second"},
                {"code": "LCE-SOC 310", "title": "Demography and Population Studies", "units": 2, "semester": "second", "is_elective": True},
                {"code": "LCE-SOC 312", "title": "Sociology of Medicine, Health and Illness", "units": 1, "semester": "second", "is_elective": True},
            ],
            "400": [
                # First Semester
                {"code": "SSC 401", "title": "Research Method II", "units": 2, "semester": "first"},
                {"code": "SOC 401", "title": "Classical and Contemporary Sociological Theories", "units": 3, "semester": "first"},
                {"code": "SOC 403", "title": "Regional Ethnography", "units": 2, "semester": "first"},
                {"code": "SOC 407", "title": "Sociology of Development", "units": 3, "semester": "first"},
                {"code": "LCE-SOC 407", "title": "Sociology of Poverty Eradication", "units": 2, "semester": "first"},
                {"code": "LCE-SOC 409", "title": "Urbanization and Labour Migration", "units": 2, "semester": "first", "is_elective": True},
                {"code": "LCE-SOC 411", "title": "Gender and Sexuality Studies", "units": 1, "semester": "first", "is_elective": True},
                {"code": "LCE-SOC 413", "title": "Sociology of Youth and Sports", "units": 1, "semester": "first", "is_elective": True},
                # Second Semester
                {"code": "SOC 408", "title": "Research Project", "units": 6, "semester": "second"},
                {"code": "SOC 406", "title": "Models in Sociological Analysis", "units": 3, "semester": "second"},
                {"code": "LCE-SOC 406", "title": "Sociology of Decolonization", "units": 2, "semester": "second"},
                {"code": "LCE-SOC 408", "title": "Industrial Sociology and Human Resource Management", "units": 2, "semester": "second"},
                {"code": "LCE-SOC 410", "title": "Seminar in Social Problems and Public Policy", "units": 2, "semester": "second"},
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
                # Handle our special link codes for repeated courses
                if "_LINK_SEM2" in original_code:
                    real_code = original_code.replace("_LINK_SEM2", "")
                    safe_code = get_safe_code(real_code, faculty.programme_type)
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
                        "semester": c["semester"], # This gets updated, but for shared it's fine
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
                    # For shared courses in both semesters, we'll just use the one provided
                    defaults={"is_active": True}
                )
                if o_created:
                    self.stdout.write(f"   Linked {course.code} to {dept.name} @ {level.display_name}")
                else:
                    self.stdout.write(f"   Offering already exists for {course.code} in {dept.name}")

        if not dry_run:
            self.stdout.write(self.style.SUCCESS("\nSuccessfully processed Sociology curriculum."))
