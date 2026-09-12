from django.core.management.base import BaseCommand
from accounts.models import (
    Faculty, Department, Level, AcademicSession, Course, CourseOffering, User
)

class Command(BaseCommand):
    help = "Upload Mathematics Education courses for all levels (100-400)"

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

        # 1. Faculty & Department
        faculty, f_created = Faculty.objects.get_or_create(
            name="Faculty of Education",
            programme_type="degree"
        )
        if f_created: self.stdout.write(f"Created Faculty: {faculty.name}")

        dept, d_created = Department.objects.get_or_create(
            name="Mathematics Education",
            faculty=faculty,
            defaults={"short_name": "MED"}
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
                {"code": "GST 111", "title": "Communication in English", "units": 2, "semester": "first"},
                {"code": "EDU 101", "title": "Introduction to Teaching and Foundations of Education", "units": 2, "semester": "first"},
                {"code": "SED 101", "title": "Introduction of Mathematics and Mathematics Education", "units": 2, "semester": "first"},
                {"code": "MTH 101", "title": "Elementary Mathematics I", "units": 2, "semester": "first"},
                {"code": "MTH 103", "title": "Elementary Mathematics III", "units": 2, "semester": "first"},
                {"code": "COS 101", "title": "Introduction to Computer Science", "units": 3, "semester": "first"},
                {"code": "PHY 101", "title": "General Physics I", "units": 2, "semester": "first"},
                {"code": "LCE-SED 101", "title": "History and Philosophy of Science Subjects and Mathematics", "units": 2, "semester": "first"},
                # Second Semester
                {"code": "GST 112", "title": "Nigerian Peoples and Culture", "units": 2, "semester": "second"},
                {"code": "MTH 102", "title": "Elementary Mathematics II", "units": 2, "semester": "second"},
                {"code": "COS 102", "title": "Problem Solving", "units": 3, "semester": "second"},
                {"code": "STA 112", "title": "Probability I", "units": 3, "semester": "second"},
                {"code": "STA 122", "title": "Statistical Computing", "units": 3, "semester": "second"},
                {"code": "PHY 102", "title": "General Physics II", "units": 2, "semester": "second"},
                {"code": "LCE-SED 102", "title": "Foundation of Science Education", "units": 2, "semester": "second"},
                {"code": "LCE-EDU 102", "title": "Educational Psychology & Child Development", "units": 2, "semester": "second"},
            ],
            "200": [
                # First Semester
                {"code": "ENT 211", "title": "Entrepreneurship and Innovation", "units": 2, "semester": "first"},
                {"code": "EDU 201", "title": "Curriculum Delivery and General Teaching methods", "units": 2, "semester": "first"},
                {"code": "COS 201", "title": "Computer Programming I", "units": 3, "semester": "first"},
                {"code": "MTH 201", "title": "Mathematical Methods I", "units": 2, "semester": "first"},
                {"code": "MTH 203", "title": "Sets Logic and Algebra I", "units": 2, "semester": "first"},
                {"code": "MTH 205", "title": "Linear Algebra II", "units": 1, "semester": "first"},
                {"code": "MTH 207", "title": "Real Analysis I", "units": 2, "semester": "first"},
                {"code": "MTH 209", "title": "Introduction to Numerical Analysis", "units": 2, "semester": "first"},
                {"code": "LCE-SED 201", "title": "School Science and Mathematics Laboratory", "units": 2, "semester": "first"},
                {"code": "LCE-SED 203", "title": "ICT in Science Education", "units": 2, "semester": "first"},
                {"code": "LCE-SED 205", "title": "Basic Mathematics for Science Education", "units": 2, "semester": "first"},
                # Second Semester
                {"code": "GST 212", "title": "Philosophy, Logic and Human Existence", "units": 2, "semester": "second"},
                {"code": "MTH 202", "title": "Elementary Differential Equations", "units": 2, "semester": "second"},
                {"code": "MTH 204", "title": "Linear Algebra I", "units": 2, "semester": "second"},
                {"code": "COS 202", "title": "Computer Programming II", "units": 3, "semester": "second"},
                {"code": "LCE-SEM 202", "title": "Methods of Mathematics Teaching I", "units": 2, "semester": "second"},
                {"code": "LCE-EDU 202", "title": "Educational Technology", "units": 2, "semester": "second"},
                {"code": "LCE-EDU 204", "title": "Micro-teaching: Theory and Practice", "units": 2, "semester": "second"},
            ],
            "300": [
                # First Semester
                {"code": "EDU 301", "title": "Teaching Practice I", "units": 3, "semester": "first"},
                {"code": "MTH 301", "title": "Metric Space Topology", "units": 2, "semester": "first"},
                {"code": "MTH 303", "title": "Vector and Tensor Analysis", "units": 2, "semester": "first"},
                {"code": "MTH 305", "title": "Complex Analysis I", "units": 2, "semester": "first"},
                {"code": "MTH 307", "title": "Real Analysis II", "units": 2, "semester": "first"},
                {"code": "MTH 309", "title": "Introduction to Mathematical Modelling", "units": 2, "semester": "first"},
                {"code": "MTH 311", "title": "Mathematical Methods II", "units": 2, "semester": "first"},
                {"code": "MTH 313", "title": "Abstract Algebra I", "units": 2, "semester": "first"},
                {"code": "LCE-SED 305", "title": "Environmental issues in Science Education", "units": 2, "semester": "first"},
                {"code": "LCE-EDU 303", "title": "Educational Psychology of Human Learning", "units": 2, "semester": "first"},
                {"code": "LCE-EDU 305", "title": "Data Processing and Analysis in Education", "units": 2, "semester": "first"},
                # Second Semester
                {"code": "GST 312", "title": "Peace and Conflict Resolution", "units": 2, "semester": "second"},
                {"code": "ENT 312", "title": "Venture Creation", "units": 2, "semester": "second"},
                {"code": "EDU 302", "title": "Educational Measurements, Tests, Research Methods and Statistics", "units": 3, "semester": "second"},
                {"code": "SEM 304", "title": "Entrepreneurship in Mathematics Education", "units": 2, "semester": "second"},
                {"code": "MTH 302", "title": "Ordinary Differential Equations", "units": 2, "semester": "second"},
                {"code": "MTH 313_S2", "title": "Abstract Algebra II", "units": 2, "semester": "second"},
                {"code": "EDU 312", "title": "Teaching Practice II", "units": 3, "semester": "second"},
                {"code": "LCE-SED 306", "title": "Nigeria Secondary School Science and Mathematics Curriculum", "units": 2, "semester": "second"},
                {"code": "LCE-EDU 307", "title": "Inclusive and Special Education", "units": 2, "semester": "second"},
            ],
            "400": [
                # First Semester
                {"code": "EDU 401", "title": "Teaching Practice II", "units": 3, "semester": "first"},
                {"code": "MTH 401", "title": "Theory of Ordinary Differential Equations", "units": 2, "semester": "first"},
                {"code": "MTH 403", "title": "Functional Analysis", "units": 2, "semester": "first"},
                {"code": "MTH 405", "title": "General Topology", "units": 2, "semester": "first"},
                {"code": "MTH 407", "title": "Mathematical Methods", "units": 2, "semester": "first"},
                {"code": "MTH 409", "title": "Complex Analysis II", "units": 2, "semester": "first"},
                {"code": "MTH 411", "title": "Abstract Algebra II", "units": 2, "semester": "first"},
                {"code": "LCE-SED 401", "title": "Seminar in Science Education", "units": 1, "semester": "first"},
                {"code": "LCE-SED 407", "title": "Assessment in Science Education", "units": 2, "semester": "first"},
                {"code": "LCE-EDU 403", "title": "Introduction to Guidance and Counselling", "units": 2, "semester": "first"},
                {"code": "LCE-EDU 405", "title": "Educational Administration and Planning", "units": 2, "semester": "first"},
                # Second Semester
                {"code": "EDU 400_MED", "title": "Project in Mathematics Education", "units": 3, "semester": "second"},
                {"code": "MTH 402", "title": "Theory Of Partial Differential Equations", "units": 2, "semester": "second"},
                {"code": "SED 402", "title": "Science/Mathematics, Technology and Society", "units": 2, "semester": "second"},
                {"code": "SEM 402", "title": "Methods of Mathematics Teaching II", "units": 2, "semester": "second"},
                {"code": "LCE-SED 408", "title": "Ethno Learning Resources for Teaching Science and Mathematics", "units": 2, "semester": "second"},
                {"code": "LCE-SEM 410", "title": "Mathematics Laboratory Techniques", "units": 2, "semester": "second"},
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
                return f"{original_code}_DEG"
            
            return original_code

        # 5. Process Levels
        for level_name, courses in courses_by_level.items():
            level = Level.objects.filter(name=level_name).first()
            if not level:
                self.stdout.write(self.style.ERROR(f"Level '{level_name}' not found!"))
                continue

            self.stdout.write(self.style.NOTICE(f"\n--- Level: {level.display_name} ---"))

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
                    self.stdout.write(f"   Offering already exists for {course.code}")

        if not dry_run:
            self.stdout.write(self.style.SUCCESS("\nSuccessfully processed Mathematics Education curriculum."))
