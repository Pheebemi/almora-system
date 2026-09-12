from django.core.management.base import BaseCommand
from accounts.models import (
    Faculty, Department, Level, AcademicSession, Course, CourseOffering, User
)

class Command(BaseCommand):
    help = "Upload Political Science courses for all levels (100-400) with Degree/Diploma separation logic"

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

        # Ensure Political Science department exists or find existing one
        dept, d_created = Department.objects.get_or_create(
            name="Political Science",
            faculty=faculty,
            defaults={"short_name": "POL"}
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
        # Note: GST 312 / ENT 312 are linked to both semesters in 300L
        courses_by_level = {
            "100": [
                # First Semester
                {"code": "PSC 101", "title": "Introduction to Political Science I", "units": 3, "semester": "first"},
                {"code": "PSC 105", "title": "Citizen and the State", "units": 2, "semester": "first"},
                {"code": "GST 111", "title": "Communication in English I", "units": 2, "semester": "first"},
                {"code": "GST 101", "title": "Use of English", "units": 2, "semester": "first"},
                {"code": "LCE-GST 103", "title": "Nigerian Constitutional Development", "units": 2, "semester": "first"},
                {"code": "LCE-PSC 107", "title": "Introduction to Jukun Politics", "units": 2, "semester": "first"},
                {"code": "LCE-PSC 109", "title": "Political Communication", "units": 2, "semester": "first"},
                {"code": "PSY 101", "title": "Introduction to Psychology", "units": 2, "semester": "first", "is_elective": True},
                # Second Semester
                {"code": "GST 112", "title": "Nigerian Peoples and Culture", "units": 2, "semester": "second"},
                {"code": "POL 102", "title": "Introduction to African Politics", "units": 2, "semester": "second"},
                {"code": "POL 104", "title": "Nigerian legal system", "units": 2, "semester": "second"},
                {"code": "LCE-GST 106", "title": "Introduction to Philosophy", "units": 2, "semester": "second"},
                {"code": "LCE-GST 104", "title": "Communication in English II", "units": 2, "semester": "second"},
                {"code": "LCE-POL 104", "title": "Constitutional Development of Nigeria", "units": 2, "semester": "second"},
                {"code": "LCE-PSC 106", "title": "Politics and Development in Jukun Kingdom", "units": 2, "semester": "second"},
                {"code": "SOC 101", "title": "Basic Sociology", "units": 2, "semester": "second", "is_elective": True}, # Mapping Basic Sociology to SOC 101 if exists
                {"code": "ECN 101", "title": "Introduction to Economics", "units": 2, "semester": "second", "is_elective": True},
            ],
            "200": [
                # First Semester
                {"code": "ENT 211", "title": "Entrepreneurship and Innovation", "units": 2, "semester": "first"},
                {"code": "POL 201", "title": "Nigerian Government and Politics", "units": 2, "semester": "first"},
                {"code": "POL 203", "title": "Political Ideas", "units": 2, "semester": "first"},
                {"code": "POL 205", "title": "Introduction to International Relations", "units": 2, "semester": "first"},
                {"code": "PSC 201", "title": "Introduction to Political Science II", "units": 3, "semester": "first"},
                {"code": "PSC 211", "title": "Nigerian Government & Politics", "units": 3, "semester": "first"},
                {"code": "SOC 101_ALT", "title": "Basic Sociology", "units": 2, "semester": "first", "is_elective": True},
                # Second Semester
                {"code": "GST 212", "title": "Philosophy, Logic and Human Existence", "units": 2, "semester": "second"},
                {"code": "SSC 202", "title": "Introduction to Computer and its Application", "units": 3, "semester": "second"},
                {"code": "POL 202", "title": "Introduction to Political Analysis", "units": 2, "semester": "second"},
                {"code": "POL 204", "title": "Foundations of Political Economy", "units": 2, "semester": "second"},
                {"code": "POL 206", "title": "Introduction to Public Administration", "units": 2, "semester": "second"},
                {"code": "LCE-PSC 208", "title": "Legislative Politics in Taraba State, Nigeria", "units": 3, "semester": "second"},
                {"code": "ECN 101_ALT", "title": "Introduction to Economics", "units": 2, "semester": "second", "is_elective": True},
                {"code": "POL 104_ALT", "title": "Nigerian Legal System", "units": 3, "semester": "second", "is_elective": True},
            ],
            "300": [
                # First Semester
                {"code": "GST 312", "title": "Peace and Conflict Resolution", "units": 2, "semester": "first"},
                {"code": "ENT 312", "title": "Venture Creation", "units": 2, "semester": "first"},
                {"code": "SSC 301", "title": "Innovation in the Social Sciences", "units": 2, "semester": "first"},
                {"code": "POL 301", "title": "History of Political thought", "units": 2, "semester": "first"},
                {"code": "POL 303", "title": "Contemporary Political Analysis", "units": 2, "semester": "first"},
                {"code": "POL 305", "title": "Public Policy analysis", "units": 2, "semester": "first"},
                {"code": "POL 307", "title": "Statistics for Political Science", "units": 2, "semester": "first"},
                {"code": "POL 309", "title": "Theories of International Relations", "units": 2, "semester": "first"},
                {"code": "LCE-PSC 309", "title": "Political Economy of North East Nigeria", "units": 3, "semester": "first"},
                {"code": "LCE-PSC 313", "title": "North East Women in Nigerian Politics.", "units": 2, "semester": "first"},
                # Second Semester
                {"code": "GST 312_LINK_SEM2", "title": "Peace and Conflict Resolution", "units": 2, "semester": "second"},
                {"code": "ENT 312_LINK_SEM2", "title": "Venture Creation", "units": 2, "semester": "second"},
                {"code": "SSC 302", "title": "Research Method I", "units": 2, "semester": "second"},
                {"code": "POL 312", "title": "Theory and Practice of Marxism", "units": 2, "semester": "second"},
                {"code": "POL302", "title": "Logic and Methods of Political Science Research", "units": 2, "semester": "second"},
                {"code": "POL 304", "title": "Political Behaviour", "units": 2, "semester": "second"},
                {"code": "POL 306", "title": "Comparative Federalism", "units": 2, "semester": "second"},
                {"code": "POL 308", "title": "Politics of development and underdevelopment", "units": 2, "semester": "second"},
                {"code": "POL 310", "title": "Democratization Studies", "units": 2, "semester": "second"},
                {"code": "LCE-PSC 310", "title": "Peace and Conflict in Northeast Nigeria", "units": 2, "semester": "second"},
                {"code": "LCE-PSC 316", "title": "Community Participation in Development", "units": 2, "semester": "second"},
                {"code": "LCE-PSC 318", "title": "Peace and Conflict Management", "units": 2, "semester": "second"},
            ],
            "400": [
                # First Semester
                {"code": "SSC 401", "title": "Research Method II", "units": 2, "semester": "first"},
                {"code": "POL 401", "title": "Civil-Military Relations", "units": 2, "semester": "first"},
                {"code": "POL403", "title": "Contemporary Defence and Strategic Studies", "units": 2, "semester": "first"},
                {"code": "POL 405", "title": "Nigerian Foreign Policy", "units": 2, "semester": "first"},
                {"code": "POL 407", "title": "Research Project", "units": 4, "semester": "first"},
                {"code": "LCE-PSC 409", "title": "The Politics of Insurgency in Northeast Nigeria", "units": 2, "semester": "first"},
                {"code": "LCE-PSC 411", "title": "International Politics of Lake Chad Basin.", "units": 2, "semester": "first"},
                # Second Semester
                {"code": "POL 408", "title": "Political Sociology", "units": 2, "semester": "second"},
                {"code": "POL 402", "title": "State and Economy", "units": 2, "semester": "second"},
                {"code": "POL 404", "title": "Nigerian Local Government System", "units": 2, "semester": "second"},
                {"code": "POL 406", "title": "International Law and Organization", "units": 2, "semester": "second"},
                {"code": "POL 410", "title": "Political Parties and Pressure Groups", "units": 2, "semester": "second"},
                {"code": "LCE-PSC 414", "title": "Politics of Revenue Generation in Taraba State.", "units": 3, "semester": "second"},
                {"code": "LCE-PSC 416", "title": "Issues in Northeast Security", "units": 2, "semester": "second"},
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
                if "_LINK_SEM2" in original_code:
                    real_code = original_code.replace("_LINK_SEM2", "")
                    safe_code = get_safe_code(real_code, faculty.programme_type)
                elif "_ALT" in original_code:
                    real_code = original_code.replace("_ALT", "")
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
            self.stdout.write(self.style.SUCCESS("\nSuccessfully processed Political Science curriculum."))
