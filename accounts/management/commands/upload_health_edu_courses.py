from django.core.management.base import BaseCommand
from accounts.models import (
    Faculty, Department, Level, AcademicSession, Course, CourseOffering, User
)

class Command(BaseCommand):
    help = "Upload Health Education courses for all levels (100-400)"

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
        # Faculty of Education should exist from BED upload
        faculty, f_created = Faculty.objects.get_or_create(
            name="Faculty of Education",
            programme_type="degree"
        )
        if f_created: self.stdout.write(f"Created Faculty: {faculty.name}")

        dept, d_created = Department.objects.get_or_create(
            name="Health Education",
            faculty=faculty,
            defaults={"short_name": "HED"}
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
                {"code": "BIO 101", "title": "General Biology I", "units": 2, "semester": "first"},
                {"code": "EDU 101", "title": "Introduction to Teaching and Education Foundation", "units": 2, "semester": "first"},
                {"code": "HED 101", "title": "Introduction to Health Education", "units": 3, "semester": "first"},
                {"code": "HED 105", "title": "Personal Health & Dental Education", "units": 2, "semester": "first"},
                {"code": "PED 101", "title": "Skill Development & Techniques of (Track & Field Events)", "units": 3, "semester": "first"},
                {"code": "HED 107", "title": "Human Growth and Development", "units": 2, "semester": "first"},
                {"code": "LCE-HED 103", "title": "Human Anatomy and Physiology I", "units": 3, "semester": "first"},
                # Second Semester
                {"code": "GST 112", "title": "Nigerian Peoples and Culture", "units": 2, "semester": "second"},
                {"code": "LCE-EHE 120", "title": "Introduction to Community and Public Health", "units": 2, "semester": "second"},
                {"code": "HED 104", "title": "Environmental Health", "units": 2, "semester": "second"},
                {"code": "HED 106", "title": "Health Education as a Profession", "units": 2, "semester": "second"},
                {"code": "LCE-HED 108", "title": "Health and Illness Behavior", "units": 2, "semester": "second"},
                {"code": "LCE-EDU 102", "title": "Educational Psychology", "units": 2, "semester": "second"},
                {"code": "LCE-BIO 108", "title": "Biology Practical", "units": 1, "semester": "second"},
                {"code": "LCE-HED 110", "title": "Basics activities in Health Education", "units": 2, "semester": "second", "is_elective": True},
            ],
            "200": [
                # First Semester
                {"code": "ENT 211", "title": "Entrepreneurship and Innovation", "units": 2, "semester": "first"},
                {"code": "EDU 201", "title": "Curriculum, Curriculum Delivery and Teaching Methods", "units": 2, "semester": "first"},
                {"code": "EHE 211", "title": "Methods and Resources in Health Education", "units": 2, "semester": "first"},
                {"code": "EHE 213", "title": "Human Anatomy and Physiology", "units": 2, "semester": "first"},
                {"code": "EHE 215", "title": "Family Life, Reproductive Health & Population Education", "units": 2, "semester": "first"},
                {"code": "EHE 219", "title": "Health Education Practicum", "units": 2, "semester": "first"},
                {"code": "HED 207", "title": "Methods and Resources in Health Education", "units": 2, "semester": "first"},
                {"code": "LCE-HED 213", "title": "Allergies & Management in Children and Youth", "units": 2, "semester": "first"},
                {"code": "LCE-HED 201", "title": "Drug Education", "units": 2, "semester": "first", "is_elective": True},
                # Second Semester
                {"code": "GST 212", "title": "Philosophy, Logic and Human Existence", "units": 2, "semester": "second"},
                {"code": "EHE 212", "title": "School Health Education Programme", "units": 2, "semester": "second"},
                {"code": "EHE 220", "title": "Food and Human Nutrition", "units": 2, "semester": "second"},
                {"code": "EHE 222", "title": "Emotional, Mental and Social Health", "units": 2, "semester": "second"},
                {"code": "HED 218", "title": "Human Diseases & Health Protection", "units": 2, "semester": "second"},
                {"code": "HED 212", "title": "School Health Education Programme", "units": 2, "semester": "second"},
                {"code": "HED 202", "title": "Community Health Education", "units": 2, "semester": "second"},
                {"code": "LCE-EDU 204", "title": "Micro Teaching, Theory and Practice", "units": 2, "semester": "second"},
                {"code": "EDU 202", "title": "Educational Technology", "units": 2, "semester": "second"},
                {"code": "LCE-HED 210", "title": "Health Agencies and Programme", "units": 2, "semester": "second", "is_elective": True},
                {"code": "LCE-EDU 206", "title": "Skills & Techniques of Team and Individual Sports (Basketball & Tennis) II", "units": 2, "semester": "second", "is_elective": True},
            ],
            "300": [
                # First Semester
                {"code": "EDU 301", "title": "Teaching Practice I", "units": 3, "semester": "first"},
                {"code": "EHE 313", "title": "Research Methods in Health Education", "units": 2, "semester": "first"},
                {"code": "EHE 315", "title": "Maternal, Infant & Child Health", "units": 2, "semester": "first"},
                {"code": "EHE 317", "title": "Health Psychology and Counselling", "units": 2, "semester": "first"},
                {"code": "EHE 321", "title": "Application of Computer Skills & Informatics in Health Education", "units": 2, "semester": "first"},
                {"code": "HED 309", "title": "Health Psychology and Counselling", "units": 2, "semester": "first"},
                {"code": "HED 307", "title": "Comparative Healthcare Delivery System", "units": 2, "semester": "first"},
                {"code": "LCE-HED 305", "title": "Vital Statistics in Health", "units": 2, "semester": "first", "is_elective": True},
                {"code": "LCE-HED 311", "title": "Environmental Stress Condition and Acclimatization", "units": 2, "semester": "first", "is_elective": True},
                # Second Semester
                {"code": "GST 312", "title": "Peace and Conflict Resolution", "units": 2, "semester": "second"},
                {"code": "ENT 312", "title": "Venture Creation", "units": 2, "semester": "second"},
                {"code": "EDU 302", "title": "Educational Measurements, Tests, Research Methods and Statistics", "units": 3, "semester": "second"},
                {"code": "EHE 314", "title": "Substance Use and Abuse Prevention", "units": 2, "semester": "second"},
                {"code": "EHE 320", "title": "First Aid, Accident Prevention and Safety Education", "units": 2, "semester": "second"},
                {"code": "EHE 322", "title": "Life Skills & Skilled-Based Health Education", "units": 2, "semester": "second"},
                {"code": "EHE 324", "title": "Epidemiology of Public Health & Human Biometrics", "units": 2, "semester": "second"},
                {"code": "HED 304", "title": "Adolescent and Adult Health Education", "units": 2, "semester": "second"},
                {"code": "HED 308", "title": "Allergies and management in Children and Youth", "units": 2, "semester": "second"},
                {"code": "HED 302", "title": "Mental Health Education", "units": 2, "semester": "second", "is_elective": True},
            ],
            "400": [
                # First Semester
                {"code": "EDU 401", "title": "Teaching Practice II", "units": 3, "semester": "first"},
                {"code": "EHE 401", "title": "Contemporary National Health Programme, Issues and Problems in Public Health", "units": 2, "semester": "first"},
                {"code": "EHE 403", "title": "Health Economics & Consumerism", "units": 2, "semester": "first"},
                {"code": "EHE 407", "title": "Seminar in Health Education", "units": 2, "semester": "first"},
                {"code": "EHE 409", "title": "Curriculum Development & Innovation in Health Education", "units": 2, "semester": "first"},
                {"code": "EDU 400_HED", "title": "Project", "units": 3, "semester": "first"}, # Clarified from user text
                {"code": "LCE-HED 405", "title": "Health System Research", "units": 2, "semester": "first"},
                {"code": "HED 407", "title": "Nigeria National Health Policy", "units": 2, "semester": "first"},
                {"code": "LCE-HED 411F", "title": "Environmental Health Education", "units": 2, "semester": "first"},
                {"code": "LCE-HED 411", "title": "Healthcare Delivery System", "units": 2, "semester": "first", "is_elective": True},
                # Second Semester
                {"code": "EDU 400_HED_S2", "title": "Project", "units": 3, "semester": "second"},
                {"code": "EHE 402", "title": "Occupational and Industrial Health", "units": 2, "semester": "second"},
                {"code": "EHE 404", "title": "Organization, Planning and Evaluation of Health Education Programme", "units": 2, "semester": "second"},
                {"code": "EHE 408", "title": "Global Health, National Health Laws, Policies and Advocacy", "units": 2, "semester": "second"},
                {"code": "HED 402", "title": "Occupational and Industrial Health", "units": 2, "semester": "second"},
                {"code": "HED 410", "title": "Geriatrics & Death Education", "units": 2, "semester": "second"},
                {"code": "HED 416", "title": "Major Contemporary National Health Programme", "units": 2, "semester": "second"},
                {"code": "HED 404", "title": "Informative Health Education", "units": 2, "semester": "second"},
                {"code": "LCE-HED 410", "title": "International and Career in Health", "units": 2, "semester": "second"},
                {"code": "HED 408", "title": "Primary Healthcare System in Nigeria", "units": 2, "semester": "second"},
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
            self.stdout.write(self.style.SUCCESS("\nSuccessfully processed Health Education curriculum."))
