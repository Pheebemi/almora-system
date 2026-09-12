from django.core.management.base import BaseCommand
from accounts.models import (
    Faculty, Department, Level, AcademicSession, Course, CourseOffering, User
)

class Command(BaseCommand):
    help = "Upload Islamic Religious Studies courses for all levels (100-400)"

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
        # Faculty of Arts should exist from previous upload, but get_or_create for safety
        faculty, f_created = Faculty.objects.get_or_create(
            name="Faculty of Arts",
            programme_type="degree"
        )
        if f_created: self.stdout.write(f"Created Faculty: {faculty.name}")

        dept, d_created = Department.objects.get_or_create(
            name="Islamic Religious Studies",
            faculty=faculty,
            defaults={"short_name": "IRS"}
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
                {"code": "GST 111", "title": "Communication in English I", "units": 2, "semester": "first"},
                {"code": "GST 113", "title": "Nigerian Peoples and Cultures", "units": 2, "semester": "first"},
                {"code": "ARA 101", "title": "Arabic Language Drills", "units": 2, "semester": "first"},
                {"code": "ISS 101", "title": "Early History of Islam, from Jahiliyyah Period to the Death of the Prophet (SAW) - 632 CE", "units": 3, "semester": "first"},
                {"code": "ISS 103", "title": "Studies on the Quran", "units": 2, "semester": "first"},
                {"code": "ISS 105", "title": "Introduction to the Hadith", "units": 2, "semester": "first"},
                {"code": "ISL 105", "title": "Introduction to Computer", "units": 3, "semester": "first"},
                {"code": "ISS 107", "title": "Introduction to Islamic Philosophy", "units": 2, "semester": "first"},
                # Second Semester
                {"code": "GST 111_IRS_S2", "title": "Communication in English II", "units": 2, "semester": "second"},
                {"code": "IRS 10", "title": "Quranic Studies I", "units": 3, "semester": "second"},
                {"code": "ISS 102", "title": "Tawhid and Ibadat (Faith and Worship in Islam)", "units": 2, "semester": "second"},
                {"code": "ISL 102", "title": "Islamic Terminologies", "units": 3, "semester": "second"},
                {"code": "ISL 110", "title": "Islamic Cities", "units": 3, "semester": "second"},
                {"code": "ISS 104", "title": "Islam and Africa", "units": 3, "semester": "second"},
                {"code": "ISS 106", "title": "Basis of Islamic Thought and Civilization", "units": 3, "semester": "second"},
                {"code": "ISS 108", "title": "Islamic Education", "units": 2, "semester": "second"},
            ],
            "200": [
                # First Semester
                {"code": "ENT 211", "title": "Entrepreneurship and Innovation", "units": 2, "semester": "first"},
                {"code": "FAC 201", "title": "Digital Humanities: Application of Computer to the Arts", "units": 3, "semester": "first"},
                {"code": "ISS 201", "title": "Early Muslim Philosophers", "units": 2, "semester": "first"},
                {"code": "ISS 203", "title": "Sources and Development of the Shariah (Islamic Law)", "units": 3, "semester": "first"},
                {"code": "ISS 205", "title": "Textual Studies of the Quran I", "units": 2, "semester": "first"},
                {"code": "ISS 207", "title": "Islam and Gender Studies", "units": 3, "semester": "first"},
                {"code": "ISL 211", "title": "ICT and Islam", "units": 3, "semester": "first"},
                {"code": "GST 203", "title": "Nigeria Peoples and Culture/Citizenship", "units": 2, "semester": "first"},
                # Second Semester
                {"code": "GST 212_IRS", "title": "Philosophy, Logic and Human Existence", "units": 2, "semester": "second"},
                {"code": "FAC 202_IRS", "title": "The Arts and Other Disciplines", "units": 2, "semester": "second"},
                {"code": "LCE-IRS 202", "title": "Islamic Theology", "units": 3, "semester": "second"},
                {"code": "LCE-IRS 204", "title": "Arabic Language II", "units": 3, "semester": "second"},
                {"code": "ISS 202", "title": "Islamic Family Law", "units": 2, "semester": "second"},
                {"code": "GST 206", "title": "Peace and Conflict", "units": 2, "semester": "second"},
                {"code": "ISL 206", "title": "Contemporary Muslim Society", "units": 2, "semester": "second"},
                {"code": "ISL 2210", "title": "Classical Research and Scholarship", "units": 2, "semester": "second"},
                {"code": "ISS 204", "title": "History of Islam, from the Four Rightly-guided Caliphs to the Abbasid Era", "units": 2, "semester": "second"},
                {"code": "ISS 206", "title": "Textual Studies of the Hadith I", "units": 2, "semester": "second"},
            ],
            "300": [
                # First Semester
                {"code": "FAC 301_IRS", "title": "Research Methods in the Arts", "units": 2, "semester": "first"},
                {"code": "ISS 301", "title": "Textual Studies of the Quran II", "units": 2, "semester": "first"},
                {"code": "ISS 303", "title": "Islamic Economic System", "units": 2, "semester": "first"},
                {"code": "ISS 305", "title": "History and Creed of Ahlus-Sunnah and the Shicah", "units": 2, "semester": "first"},
                {"code": "ISS 307", "title": "Moral Philosophy in Islam", "units": 2, "semester": "first"},
                {"code": "ISL 311", "title": "Comparative Studies of Religion", "units": 2, "semester": "first"},
                {"code": "ISL 307", "title": "Sufism and Tawassul", "units": 2, "semester": "first"},
                {"code": "LCE-IRS 301", "title": "Tafsir (Quranic Exegesis)", "units": 3, "semester": "first"},
                {"code": "LCE-IRS 303", "title": "Islamic Ethics", "units": 3, "semester": "first"},
                # Second Semester
                {"code": "GST 312_IRS", "title": "Peace and Conflict Resolution", "units": 2, "semester": "second"},
                {"code": "ENT 312_IRS", "title": "Venture Creation", "units": 2, "semester": "second"},
                {"code": "FAC 302_IRS", "title": "Theories in the Arts and Humanities", "units": 2, "semester": "second"},
                {"code": "ISS 302", "title": "Textual Studies of the Hadith II", "units": 2, "semester": "second"},
                {"code": "ISS 304", "title": "Shariah: al Uqubat (Penal codes)", "units": 2, "semester": "second"},
                {"code": "ISS 306", "title": "Entrepreneurial Skills in Islamic Studies (Calligraphy)", "units": 3, "semester": "second"},
                {"code": "ISL 308", "title": "Revivalism and Revivalist Movement", "units": 2, "semester": "second"},
                {"code": "ISL 310", "title": "Advance Studies on Islamic Theology", "units": 3, "semester": "second"},
                {"code": "ISS 308", "title": "Islamic Political Thought and Movements", "units": 2, "semester": "second"},
            ],
            "400": [
                # First Semester
                {"code": "ISS 401", "title": "Fiqh of Contemporary Issues", "units": 3, "semester": "first"},
                {"code": "ISS 403", "title": "Islamic Contributions to the Renaissance", "units": 3, "semester": "first"},
                {"code": "ISS 405", "title": "Islam in Nigeria", "units": 3, "semester": "first"},
                {"code": "ISS 407", "title": "Long Essay/Project", "units": 6, "semester": "first"},
                {"code": "ISL 407", "title": "Textual Studies of the Quran and Hadith", "units": 2, "semester": "first"},
                {"code": "ISL 411", "title": "Advance Studies of Creed of Al-Sunnah", "units": 2, "semester": "first"},
                {"code": "ISL 413", "title": "Heretical Movement According to Islam", "units": 2, "semester": "first"},
                # Second Semester
                {"code": "ISS 402", "title": "Advanced Study of Muslim Law", "units": 3, "semester": "second"},
                {"code": "ISS 404", "title": "Qadiriyyah and Tijaniyyah", "units": 3, "semester": "second"},
                {"code": "ISS 406", "title": "Islam and Pluralism", "units": 3, "semester": "second"},
                {"code": "ISS 407_S2", "title": "Long Essay/Project", "units": 6, "semester": "second"},
                {"code": "ISL 412", "title": "Selected Topics from the Quran", "units": 3, "semester": "second"},
                {"code": "ISL 406", "title": "Sokoto Caliphate Literature", "units": 2, "semester": "second"},
                {"code": "ISL 404", "title": "Islam in Kanem Borno", "units": 2, "semester": "second"},
                {"code": "ISL 414", "title": "Islam Literature Vernacular", "units": 2, "semester": "second"},
            ]
        }

        # 4. Helper to resolve cross-programme/clash code collisions
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
                # Suffix handling for internal clashes or cross-dept unit clashes
                # FAC 201 is 3 units here, but 2 units in ENG. So we need a suffix.
                if original_code == "FAC 201":
                    safe_code = "FAC 201_IRS"
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
                    self.stdout.write(f"   Offering already exists for {course.code}")

        if not dry_run:
            self.stdout.write(self.style.SUCCESS("\nSuccessfully processed Islamic Studies curriculum."))
