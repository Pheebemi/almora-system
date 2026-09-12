from django.core.management.base import BaseCommand
from accounts.models import (
    Faculty, Department, Level, AcademicSession, Course, CourseOffering, User
)

class Command(BaseCommand):
    help = "Upload Biology Education courses for all levels (100-400)"

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
            name="Biology Education",
            faculty=faculty,
            defaults={"short_name": "BED"}
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
                {"code": "BIO 101", "title": "General Biology I", "units": 2, "semester": "first"},
                {"code": "BIO 107", "title": "General Biology Practical I", "units": 1, "semester": "first"},
                {"code": "COS 101", "title": "Introduction to Computer Science", "units": 3, "semester": "first"},
                {"code": "CHM 101", "title": "General Chemistry I (Inorganic)", "units": 2, "semester": "first"},
                {"code": "MTH 101", "title": "General Mathematics I", "units": 2, "semester": "first"},
                {"code": "PHY 101", "title": "General Physics I", "units": 2, "semester": "first"},
                {"code": "LCE-SED 101", "title": "History and Philosophy of Science Subjects and Mathematics", "units": 2, "semester": "first"},
                # Second Semester
                {"code": "GST 112", "title": "Nigerian Peoples and Culture", "units": 2, "semester": "second"},
                {"code": "BIO 102", "title": "General Biology II", "units": 2, "semester": "second"},
                {"code": "BIO 108", "title": "General Biology Practical II", "units": 1, "semester": "second"},
                {"code": "CHM 102", "title": "General Chemistry II (Organic)", "units": 2, "semester": "second"},
                {"code": "MTH 102", "title": "General Mathematics II", "units": 2, "semester": "second"},
                {"code": "PHY 102", "title": "General Physics II", "units": 2, "semester": "second"},
                {"code": "LCE-SED 102", "title": "Foundation of Science Education", "units": 2, "semester": "second"},
                {"code": "LCE-EDU 102", "title": "Educational Psychology & Child Development", "units": 2, "semester": "second"},
            ],
            "200": [
                # First Semester
                {"code": "ENT 211", "title": "Entrepreneurship and Innovations", "units": 2, "semester": "first"},
                {"code": "EDU 201", "title": "Curriculum Delivery and General Teaching Methods", "units": 2, "semester": "first"},
                {"code": "BIO 201", "title": "Genetics I", "units": 2, "semester": "first"},
                {"code": "BIO 203", "title": "General Physiology", "units": 2, "semester": "first"},
                {"code": "BIO 205", "title": "Introductory Developmental/Cell Biology", "units": 2, "semester": "first"},
                {"code": "BCH 201", "title": "General Biochemistry", "units": 2, "semester": "first"},
                {"code": "MCB 221", "title": "General Microbiology", "units": 2, "semester": "first"},
                {"code": "LCE-SED 201", "title": "School Science and Mathematics Laboratory", "units": 2, "semester": "first"},
                {"code": "LCE-SED 203", "title": "ICT in Science Education", "units": 2, "semester": "first"},
                {"code": "LCE-SED 205", "title": "Basic Mathematics for Science Education", "units": 2, "semester": "first"},
                # Second Semester
                {"code": "GST 212", "title": "Philosophy, Logic and Human Existence", "units": 2, "semester": "second"},
                {"code": "BIO 202", "title": "Introductory Ecology", "units": 2, "semester": "second"},
                {"code": "BIO 204", "title": "Biological Techniques", "units": 3, "semester": "second"},
                {"code": "BIO 206", "title": "Hydrobiology", "units": 2, "semester": "second"},
                {"code": "BIO 208", "title": "Biostatistics", "units": 3, "semester": "second"},
                {"code": "LCE-SEB 202", "title": "General Biology Method I", "units": 3, "semester": "second"},
                {"code": "LCE-EDU 202", "title": "Educational Technology", "units": 2, "semester": "second"},
                {"code": "LCE-EDU 204", "title": "Micro-teaching: Theory and Practice", "units": 3, "semester": "second"},
            ],
            "300": [
                # First Semester
                {"code": "EDU 301", "title": "Teaching Practice I", "units": 3, "semester": "first"},
                {"code": "BIO 301", "title": "Genetics II", "units": 2, "semester": "first"},
                {"code": "BIO 303", "title": "Biogeography and Soil Biology", "units": 2, "semester": "first"},
                {"code": "BIO 305", "title": "Systematic Biology", "units": 2, "semester": "first"},
                {"code": "BIO 307", "title": "Field Course", "units": 2, "semester": "first"},
                {"code": "LCE-SED 305", "title": "Environmental issues in Science Education", "units": 2, "semester": "first"},
                {"code": "LCE-EDU 303", "title": "Educational Psychology of Human Learning", "units": 2, "semester": "first"},
                {"code": "LCE-EDU 305", "title": "Data Processing and Analysis in Education", "units": 3, "semester": "first"},
                {"code": "LCE-EDU 307", "title": "Inclusive and Special Education", "units": 2, "semester": "first"},
                # Second Semester
                {"code": "GST 312", "title": "Peace and Conflict Resolution", "units": 2, "semester": "second"},
                {"code": "ENT 312", "title": "Venture Creation", "units": 2, "semester": "second"},
                {"code": "EDU 302", "title": "Educational Measurements, Tests, Research Methods and Statistics", "units": 3, "semester": "second"},
                {"code": "SEB 302", "title": "General Biology Methods II", "units": 3, "semester": "second"},
                {"code": "LCE-SEB 310", "title": "Biology Laboratory Techniques", "units": 2, "semester": "second"},
                {"code": "LCE-SED 306", "title": "Nigeria Secondary School Science and Mathematics Curriculum", "units": 2, "semester": "second"},
                {"code": "LCE-BIO 302", "title": "Insects and People", "units": 3, "semester": "second", "is_elective": True},
                {"code": "LCE-BIO 304", "title": "Ethno Biology", "units": 3, "semester": "second", "is_elective": True},
            ],
            "400": [
                # First Semester
                {"code": "EDU 401", "title": "Teaching Practice II", "units": 3, "semester": "first"},
                {"code": "BIO 401C", "title": "Population Biology and Evolution", "units": 2, "semester": "first"},
                {"code": "BIO 403C", "title": "Wildlife Conservation and Management", "units": 2, "semester": "first"},
                {"code": "BIO 405C", "title": "Nigerian Flora and Fauna", "units": 2, "semester": "first"},
                {"code": "BIO 407C", "title": "Field Course II", "units": 1, "semester": "first"},
                {"code": "BIO 413C", "title": "Bioinformatics", "units": 2, "semester": "first"},
                {"code": "LCE-SED 401", "title": "Seminar in Science Education", "units": 1, "semester": "first"},
                {"code": "LCE-SED 407", "title": "Assessment in Science Education", "units": 2, "semester": "first"},
                {"code": "LCE-EDU 403", "title": "Introduction to Guidance and Counselling", "units": 2, "semester": "first"},
                {"code": "LCE-EDU 405", "title": "Educational Administration and Planning", "units": 2, "semester": "first"},
                # Second Semester
                {"code": "EDU 400", "title": "Project", "units": 3, "semester": "second"},
                {"code": "SED 402", "title": "Science/Mathematics, Technology and Society", "units": 2, "semester": "second"},
                {"code": "BIO 402", "title": "Principles of Plant and Animal Breeding", "units": 2, "semester": "second"},
                {"code": "BIO 404", "title": "Nigerian Plants and Animals in Prophylactics & Therapeutics", "units": 2, "semester": "second"},
                {"code": "BIO 406", "title": "Principles of Pest Management", "units": 2, "semester": "second"},
                {"code": "BIO 408", "title": "Applied Biotechnology", "units": 2, "semester": "second"},
                {"code": "BIO 410", "title": "Bio-Entrepreneurship Options", "units": 2, "semester": "second"},
                {"code": "BIO 414", "title": "Molecular Biology", "units": 2, "semester": "second"},
                {"code": "LCE-SED 408", "title": "Ethno Learning Resources for Teaching Science and Mathematics", "units": 2, "semester": "second"},
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
            self.stdout.write(self.style.SUCCESS("\nSuccessfully processed Biology Education curriculum."))
