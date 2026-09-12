from django.core.management.base import BaseCommand
from accounts.models import (
    Faculty, Department, Level, AcademicSession, Course, CourseOffering, User
)

class Command(BaseCommand):
    help = "Upload Business Administration courses for all levels (100-400) with Degree/Diploma separation logic"

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
        faculty = Faculty.objects.filter(name="Faculty of Management Sciences", programme_type="degree").first()
        if not faculty:
            self.stdout.write(self.style.ERROR("Faculty of Management Sciences (Degree) not found!"))
            return

        # Ensure Business Administration department exists or find existing one
        dept, d_created = Department.objects.get_or_create(
            name="Business Administration",
            faculty=faculty,
            defaults={"short_name": "BUS"}
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
                {"code": "AMS 101", "title": "Principles of Management", "units": 2, "semester": "first"},
                {"code": "AMS 103", "title": "Introduction to Computers", "units": 2, "semester": "first"},
                {"code": "BUA 101", "title": "Introduction to Business I", "units": 2, "semester": "first"},
                {"code": "LCE--BUA 103", "title": "Group Business Development", "units": 2, "semester": "first"},
                {"code": "LCE--BUA 105", "title": "Introduction to Financial Accounting I", "units": 2, "semester": "first"},
                {"code": "LCE--BUA 107", "title": "Introduction to Rural Development", "units": 2, "semester": "first"},
                {"code": "LCE--BUA 109", "title": "Elements of Modern Banking", "units": 2, "semester": "first"},
                # Second Semester
                {"code": "GST 112", "title": "Nigerian Peoples and Culture", "units": 2, "semester": "second"},
                {"code": "AMS 102", "title": "Basic Mathematics", "units": 2, "semester": "second"},
                {"code": "AMS 104", "title": "Principles of Project Management", "units": 2, "semester": "second"},
                {"code": "BUA 102", "title": "Introduction to Business II", "units": 3, "semester": "second"},
                {"code": "LCE--BUA 104", "title": "Introduction to Financial Accounting II", "units": 2, "semester": "second"},
                {"code": "LCE--BUA 106", "title": "Principles of Economics", "units": 3, "semester": "second"},
                {"code": "LCE--BUA 108", "title": "Introduction to Agribusiness", "units": 2, "semester": "second"},
            ],
            "200": [
                # First Semester
                {"code": "ENT 211", "title": "Entrepreneurship and Innovation", "units": 2, "semester": "first"},
                {"code": "BUA 201", "title": "Principles of Business Administration I", "units": 3, "semester": "first"},
                {"code": "BUA 203", "title": "Business Statistics", "units": 3, "semester": "first"},
                {"code": "BUA 205", "title": "Leadership and Governance", "units": 2, "semester": "first"},
                {"code": "MKT 213", "title": "Entrepreneurial Marketing", "units": 2, "semester": "first"},
                {"code": "MKT 220", "title": "Food & Agricultural Marketing", "units": 2, "semester": "first"},
                {"code": "MKT 221", "title": "Service and Social Marketing", "units": 2, "semester": "first"},
                {"code": "LCE--BUA 207", "title": "Elements of Marketing", "units": 2, "semester": "first"},
                {"code": "LCE--BUA 209", "title": "Produce Marketing & Sales", "units": 2, "semester": "first"},
                # Second Semester
                {"code": "GST 212", "title": "Philosophy, Logic, and Human Existence", "units": 2, "semester": "second"},
                {"code": "BUA 202", "title": "Principles of Business Administration II", "units": 3, "semester": "second"},
                {"code": "BUA 204", "title": "Quantitative Analysis in Management", "units": 3, "semester": "second"},
                {"code": "BUA 216", "title": "Introduction to Financial Management", "units": 3, "semester": "second"},
                {"code": "BUA 218", "title": "Green Management", "units": 2, "semester": "second"},
                {"code": "MKT 222", "title": "Retail & Wholesale Management", "units": 2, "semester": "second"},
                {"code": "LCE--BUA 206", "title": "Cost Accounting", "units": 2, "semester": "second"},
                {"code": "LCE--BUA 208", "title": "Business Communication", "units": 2, "semester": "second"},
                {"code": "LCE--BUA 210", "title": "Industrial and Labour Relations", "units": 2, "semester": "second"},
            ],
            "300": [
                # First Semester
                {"code": "BUA 303", "title": "Management Theory", "units": 3, "semester": "first"},
                {"code": "BUA 305", "title": "Financial Management", "units": 3, "semester": "first"},
                {"code": "BUA 313", "title": "Innovation Management", "units": 2, "semester": "first"},
                {"code": "BUA 319", "title": "E-Commerce", "units": 2, "semester": "first"},
                {"code": "BUA 321", "title": "Business Start-up", "units": 2, "semester": "first"},
                {"code": "BUA 323", "title": "Supply Chain Management", "units": 3, "semester": "first"},
                {"code": "LCE--BUA 307", "title": "Business Law", "units": 2, "semester": "first"},
                # Second Semester
                {"code": "GST 312", "title": "Peace and Conflict Resolution", "units": 2, "semester": "second"},
                {"code": "ENT 312", "title": "Venture Creation", "units": 2, "semester": "second"},
                {"code": "BUA 302", "title": "Human Behavior in Organizations", "units": 3, "semester": "second"},
                {"code": "BUA 304", "title": "Human Resource Management", "units": 3, "semester": "second"},
                {"code": "BUA 310", "title": "Production and Operation Management", "units": 3, "semester": "second"},
                {"code": "BUA 312", "title": "Small Business Management", "units": 2, "semester": "second"},
                {"code": "LCE--BUA 306", "title": "Research Methods", "units": 3, "semester": "second"},
                {"code": "LCE--BUA 308", "title": "Business Analytics Skill Development", "units": 2, "semester": "second"},
            ],
            "400": [
                # First Semester
                {"code": "BUA 401", "title": "Business Policy and Strategic Management", "units": 3, "semester": "first"},
                {"code": "BUA 409", "title": "Management Information System", "units": 2, "semester": "first"},
                {"code": "BUA 411", "title": "Analysis for Business Decision", "units": 3, "semester": "first"},
                {"code": "LCE--BUA 403", "title": "Corporate Planning", "units": 3, "semester": "first"},
                {"code": "LCE--BUA 405", "title": "Comparative Management", "units": 3, "semester": "first"},
                {"code": "LCE--BUA 499", "title": "Research Project", "units": 6, "semester": "first"},
                # Second Semester
                {"code": "BUA 402", "title": "Strategic Thinking and Problem Solving", "units": 3, "semester": "second"},
                {"code": "BUA 404", "title": "Research Project in Business Administration", "units": 6, "semester": "second"},
                {"code": "BUA 406", "title": "International Business", "units": 3, "semester": "second"},
                {"code": "BUA 420", "title": "Internship", "units": 3, "semester": "second"},
                {"code": "LCE--BUA 404", "title": "Business Modeling and Consulting", "units": 2, "semester": "second"},
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
            self.stdout.write(self.style.SUCCESS("\nSuccessfully processed Business Administration curriculum."))
