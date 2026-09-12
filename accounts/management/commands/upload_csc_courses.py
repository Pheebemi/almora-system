from django.core.management.base import BaseCommand
from accounts.models import (
    Faculty, Department, Level, AcademicSession, Course, CourseOffering, User
)

class Command(BaseCommand):
    help = "Upload Computer Science courses for all levels (100-400) with Degree/Diploma separation logic"

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
        # Using exact names verified from DB
        faculty = Faculty.objects.filter(name="Faculty of Science", programme_type="degree").first()
        if not faculty:
            self.stdout.write(self.style.ERROR("Faculty of Science (Degree) not found!"))
            return

        dept = Department.objects.filter(name="Computer Science", faculty=faculty).first()
        if not dept:
            self.stdout.write(self.style.ERROR("Computer Science department (under Faculty of Science) not found!"))
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
                {"code": "GST 111", "title": "Communication in English", "units": 2, "semester": "first"},
                {"code": "MTH 101", "title": "Elementary Mathematics I", "units": 2, "semester": "first"},
                {"code": "PHY 101", "title": "General Physics I", "units": 2, "semester": "first"},
                {"code": "PHY 107", "title": "General Practical Physics I", "units": 1, "semester": "first"},
                {"code": "STA 111", "title": "Descriptive Statistics", "units": 3, "semester": "first"},
                {"code": "COS 101", "title": "Introduction to Computing Sciences", "units": 3, "semester": "first"},
                {"code": "LCE-CSC 103", "title": "Fundamental of Programming Languages", "units": 2, "semester": "first"},
                {"code": "LCE-CSC 105", "title": "Computer Appreciation", "units": 2, "semester": "first"},
                # Second Semester
                {"code": "GST 112", "title": "Nigerian Peoples and Culture", "units": 2, "semester": "second"},
                {"code": "MTH 102", "title": "Elementary Mathematics II", "units": 2, "semester": "second"},
                {"code": "PHY 102", "title": "General Physics II", "units": 2, "semester": "second"},
                {"code": "PHY 108", "title": "General Practical Physics II", "units": 1, "semester": "second"},
                {"code": "COS 102", "title": "Problem Solving", "units": 2, "semester": "second"},
                {"code": "CSC 104", "title": "Introduction to Computer Applications", "units": 2, "semester": "second"},
                {"code": "LCE-CSC 104", "title": "Hardware System & Maintenance", "units": 3, "semester": "second"},
                {"code": "LCE-CSC 106", "title": "Introduction to Programming Language", "units": 3, "semester": "second"},
            ],
            "200": [
                # First Semester
                {"code": "ENT 211", "title": "Entrepreneurship and Innovation", "units": 2, "semester": "first"},
                {"code": "MTH 201", "title": "Mathematical Methods I", "units": 2, "semester": "first"},
                {"code": "COS 201", "title": "Computer Programming I", "units": 3, "semester": "first"},
                {"code": "CSC 203", "title": "Discrete Structures", "units": 2, "semester": "first"},
                {"code": "CSC 299", "title": "SIWES I", "units": 3, "semester": "first"},
                {"code": "IFT 211", "title": "Digital Logic Design", "units": 2, "semester": "first"},
                {"code": "SEN 201", "title": "Introduction to Software Engineering", "units": 2, "semester": "first"},
                {"code": "LCE-CSC 205", "title": "Cloud Computing", "units": 2, "semester": "first"},
                {"code": "LCE-CSC 207", "title": "Web Technology", "units": 2, "semester": "first"},
                # Second Semester
                {"code": "GST 212", "title": "Philosophy, Logic and Human Existence", "units": 2, "semester": "second"},
                {"code": "MTH 202", "title": "Elementary Differential Equations", "units": 2, "semester": "second"},
                {"code": "COS 202", "title": "Computer Programming II", "units": 3, "semester": "second"},
                {"code": "IFT 212", "title": "Computer Architecture and Organization", "units": 2, "semester": "second"},
                {"code": "LCE-CSC 214", "title": "System Performance Evaluation", "units": 2, "semester": "second"},
                {"code": "LCE-CSC 216", "title": "Data Science I", "units": 2, "semester": "second"},
                {"code": "LCE-CSC 218", "title": "Management Information System", "units": 2, "semester": "second"},
            ],
            "300": [
                # First Semester
                {"code": "CSC 301", "title": "Data Structures", "units": 3, "semester": "first"},
                {"code": "CSC 309", "title": "Artificial Intelligence", "units": 2, "semester": "first"},
                {"code": "CSC 399", "title": "SIWES II", "units": 3, "semester": "first"},
                {"code": "CYB 201", "title": "Introduction to Cyber security and Strategy", "units": 2, "semester": "first"},
                {"code": "ICT 305", "title": "Data Communication System & Network", "units": 3, "semester": "first"},
                {"code": "LCE-CSC 303", "title": "Survey of Programming Language", "units": 2, "semester": "first"},
                {"code": "LCE-CSC 305", "title": "Compiler Construction", "units": 2, "semester": "first"},
                {"code": "LCE-CSC 307", "title": "Human Computer Interface", "units": 2, "semester": "first"},
                {"code": "LCE-CSC 309", "title": "Data Science II", "units": 2, "semester": "first"},
                # Second Semester
                {"code": "GST 312", "title": "Peace and Conflict Resolution", "units": 2, "semester": "second"},
                {"code": "ENT 312", "title": "Venture Creation", "units": 2, "semester": "second"},
                {"code": "CSC 308", "title": "Operating Systems", "units": 3, "semester": "second"},
                {"code": "CSC 322", "title": "Computer Science Innovation and New Technologies", "units": 2, "semester": "second"},
                {"code": "DTS 304", "title": "Data Management I", "units": 3, "semester": "second"},
                {"code": "LCE-CSC 302", "title": "Research Method in Computing", "units": 2, "semester": "second"},
                {"code": "LCE-CSC 304", "title": "System Analysis and Design", "units": 2, "semester": "second"},
                {"code": "LCE-CSC 306", "title": "Computational Science, Information and Numerical Method", "units": 2, "semester": "second"},
                {"code": "LCE-CSC 308", "title": "Theory of Computing", "units": 2, "semester": "second"},
            ],
            "400": [
                # First Semester
                {"code": "COS 409", "title": "Research Methodology and Technical Report Writing", "units": 2, "semester": "first"},
                {"code": "CSC 401", "title": "Algorithms and Complexity Analysis", "units": 2, "semester": "first"},
                {"code": "CSC 497", "title": "Final Year Project I", "units": 3, "semester": "first"},
                {"code": "INS 401", "title": "Project Management", "units": 2, "semester": "first"},
                {"code": "LCE-CSC 403", "title": "Computing in Agriculture", "units": 3, "semester": "first"},
                {"code": "LCE-CSC 405", "title": "Distributed Computing System", "units": 2, "semester": "first"},
                # Second Semester
                {"code": "CSC 402", "title": "Ethics and Legal Issues in Computer Science", "units": 2, "semester": "second"},
                {"code": "CSC 498", "title": "Final Year Project II", "units": 3, "semester": "second"},
                {"code": "LCE-CSC 404", "title": "Trends in Computing", "units": 3, "semester": "second"},
                {"code": "LCE-CSC 406", "title": "Computer Graphic", "units": 2, "semester": "second"},
                {"code": "LCE-CSC 408", "title": "Modeling and simulation", "units": 2, "semester": "second"},
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
                # Collision with a different programme! 
                # Append suffix as per plan to keep Degree/Diploma students separate
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
            self.stdout.write(self.style.SUCCESS("\nSuccessfully processed Computer Science curriculum."))
