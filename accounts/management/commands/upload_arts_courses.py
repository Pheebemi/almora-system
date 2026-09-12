from django.core.management.base import BaseCommand
from accounts.models import (
    Faculty, Department, Level, AcademicSession, Course, CourseOffering, User
)

class Command(BaseCommand):
    help = "Upload Arts courses (English Language and Literature) for all levels (100-400)"

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

        # 1. Faculty & Departments
        faculty, f_created = Faculty.objects.get_or_create(
            name="Faculty of Arts",
            programme_type="degree"
        )
        if f_created: self.stdout.write(f"Created Faculty: {faculty.name}")

        eng_dept, e_created = Department.objects.get_or_create(
            name="English Language",
            faculty=faculty,
            defaults={"short_name": "ENG"}
        )
        if e_created: self.stdout.write(f"Created Department: {eng_dept.name}")

        lit_dept, l_created = Department.objects.get_or_create(
            name="Literature in English",
            faculty=faculty,
            defaults={"short_name": "LIT"}
        )
        if l_created: self.stdout.write(f"Created Department: {lit_dept.name}")

        # 2. Get active Session
        session = AcademicSession.objects.filter(is_active=True).first()
        if not session:
            self.stdout.write(self.style.ERROR("No active Academic Session found!"))
            return

        admin_user = User.objects.filter(is_superuser=True).first()

        # 3. Define Course Data
        # Format: (dept_obj, {level: [course_dict, ...]})
        curricula = [
            (eng_dept, {
                "100": [
                    # First Semester
                    {"code": "GST 111", "title": "Communication in English", "units": 2, "semester": "first"},
                    {"code": "ENG 101", "title": "Introduction to English language", "units": 2, "semester": "first"},
                    {"code": "ENG 103", "title": "Spoken English", "units": 2, "semester": "first"},
                    {"code": "ENG 105", "title": "Basic English Composition", "units": 2, "semester": "first"},
                    {"code": "ENG 107", "title": "Introduction to Poetry", "units": 2, "semester": "first"},
                    {"code": "ENG 109", "title": "Introduction to Nigerian Literature", "units": 3, "semester": "first"},
                    {"code": "ENG 111", "title": "Survey of Africa Literature I", "units": 3, "semester": "first"},
                    {"code": "ENG 113", "title": "Introduction to Fiction", "units": 3, "semester": "first"},
                    {"code": "ENG 115", "title": "Theatre & Workshop", "units": 2, "semester": "first"},
                    # Second Semester
                    {"code": "GST 112", "title": "Nigerian Peoples and Culture", "units": 2, "semester": "second"}, # Stuck to 2 units for GST consistency
                    {"code": "ENG 102", "title": "Introduction to English Language II", "units": 2, "semester": "second"},
                    {"code": "ENG 104", "title": "Introduction to Phonetic & Phonology", "units": 2, "semester": "second"},
                    {"code": "ENG 106", "title": "Practical English Drama", "units": 3, "semester": "second"},
                    {"code": "ENG 108", "title": "Introduction to Oral Literature", "units": 2, "semester": "second", "is_elective": True},
                    {"code": "ENG 110", "title": "Introduction to Creative Writing /Practical", "units": 2, "semester": "second"},
                    {"code": "ENG 112", "title": "Introduction to Drama & Theater", "units": 2, "semester": "second"},
                    {"code": "ENG 114", "title": "Computer Mediated Communication", "units": 2, "semester": "second"},
                    {"code": "ENG 116", "title": "Mother Tongue Interference & Error Language", "units": 3, "semester": "second"},
                    {"code": "ENG 118", "title": "Comparative Study of English & Jukun", "units": 3, "semester": "second"},
                ],
                "200": [
                    # First Semester
                    {"code": "GST 211", "title": "Philosophy, Logic and Human Existence", "units": 2, "semester": "first"},
                    {"code": "ENT 211", "title": "Entrepreneurship and Innovation", "units": 2, "semester": "first"},
                    {"code": "FAC 201", "title": "Digital Humanities: Application of Computer to the Arts", "units": 2, "semester": "first"},
                    {"code": "ENG 203", "title": "Introduction to General Phonetics and Phonology I", "units": 2, "semester": "first"},
                    {"code": "ENG 205", "title": "Advanced English Composition I", "units": 2, "semester": "first"},
                    {"code": "ENG 207", "title": "Varieties of English Language", "units": 2, "semester": "first"},
                    {"code": "ENG 209", "title": "Language and Society", "units": 2, "semester": "first"},
                    {"code": "ENG 211", "title": "English Morphology", "units": 2, "semester": "first"},
                    {"code": "LCE-ENG 201", "title": "Multimodal Stylistics", "units": 3, "semester": "first", "is_elective": True},
                    {"code": "LCE-ENG 203", "title": "Traditional Nigerian Poetry", "units": 3, "semester": "first", "is_elective": True},
                    # Second Semester
                    {"code": "FAC 202", "title": "The Arts and other Disciplines", "units": 3, "semester": "second"},
                    {"code": "ENG 202", "title": "Entrepreneurial English", "units": 2, "semester": "second"},
                    {"code": "ENG 204", "title": "Introduction to General Phonetics and Phonology II", "units": 3, "semester": "second"},
                    {"code": "ENG 206", "title": "Introduction to General Phonetics and Phonology II", "units": 3, "semester": "second"}, # Typo in user text?
                    {"code": "LCE-ENG 202", "title": "Northern Nigerian Literature", "units": 3, "semester": "second", "is_elective": True},
                ],
                "300": [
                    # First Semester
                    {"code": "FAC 301", "title": "Research Methodology in the Arts", "units": 2, "semester": "first"},
                    {"code": "ENG 303", "title": "Introduction to Applied Linguistics", "units": 2, "semester": "first"},
                    {"code": "ENG 304", "title": "Introduction to Semantics", "units": 3, "semester": "first"},
                    {"code": "ENG 305", "title": "The English Language in Nigeria", "units": 2, "semester": "first"},
                    {"code": "ENG 306", "title": "Discourse Analysis", "units": 2, "semester": "first"},
                    {"code": "ENG 307", "title": "The Socio-linguistics of English", "units": 2, "semester": "first"},
                    {"code": "LIT 308_ENG", "title": "Creative Writing II", "units": 2, "semester": "first"}, # Suffix for LIT dept clash
                    {"code": "LCE-ENG 301", "title": "Advance Syntax", "units": 3, "semester": "first", "is_elective": True},
                    {"code": "LCE-ENG 303", "title": "Health Communication", "units": 3, "semester": "first", "is_elective": True},
                    # Second Semester
                    {"code": "GST 312", "title": "Peace and Conflict Resolution", "units": 2, "semester": "second"},
                    {"code": "ENT 322", "title": "Venture Creation", "units": 2, "semester": "second"},
                    {"code": "FAC 302", "title": "Theory in the Humanities", "units": 2, "semester": "second"},
                    {"code": "ENG 302", "title": "Phonology of English", "units": 3, "semester": "second"},
                    {"code": "ENG 304_S2", "title": "Introduction to Semantics", "units": 3, "semester": "second"}, # Explicit semester 2 entry
                    {"code": "ENG 306_S2", "title": "Discourse Analysis", "units": 2, "semester": "second"},
                    {"code": "ENG 307_S2", "title": "The Socio-linguistics of English", "units": 2, "semester": "second"},
                    {"code": "LIT 308_ENG_S2", "title": "Creative Writing II", "units": 2, "semester": "second"},
                    {"code": "LCE-ENG 302", "title": "Forensic Linguistics", "units": 3, "semester": "second", "is_elective": True},
                    {"code": "LCE-ENG 304", "title": "Indigenous Thought Systems", "units": 3, "semester": "second", "is_elective": True},
                ],
                "400": [
                    # First Semester 
                    {"code": "ENG 403", "title": "Psycholinguistics", "units": 2, "semester": "first"},
                    {"code": "ENG 404", "title": "Multilingualism", "units": 2, "semester": "first"},
                    {"code": "ENG 405", "title": "English for Specific Purposes", "units": 2, "semester": "first"},
                    {"code": "ENG 409", "title": "Project/Long Essay", "units": 3, "semester": "first"},
                    {"code": "ENG 406", "title": "Research Methods I&II", "units": 2, "semester": "first"},
                    {"code": "LCE-ENG 401", "title": "Children’s Literature", "units": 3, "semester": "first", "is_elective": True},
                    {"code": "LCE-ENG 403", "title": "Introduction to Language Rights and Language Conflicts", "units": 3, "semester": "first", "is_elective": True},
                    # Second Semester
                    {"code": "ENG 402", "title": "Pragmatics", "units": 2, "semester": "second"},
                    {"code": "ENG 403_S2", "title": "Psycholinguistics", "units": 2, "semester": "second"},
                    {"code": "ENG 404_S2", "title": "Multilingualism", "units": 2, "semester": "second"},
                    {"code": "ENG 405_S2", "title": "English for Specific Purposes", "units": 2, "semester": "second"},
                    {"code": "ENG 409_S2", "title": "Project/Long Essay", "units": 3, "semester": "second"},
                    {"code": "ENG 406_S2", "title": "Research Methods I&II", "units": 2, "semester": "second"},
                    {"code": "LCE-ENG 402", "title": "Introduction to Language Documentation and Description", "units": 3, "semester": "second", "is_elective": True},
                    {"code": "LCE-ENG 404", "title": "Literature in the Digital Age", "units": 3, "semester": "second", "is_elective": True},
                ]
            }),
            (lit_dept, {
                "100": [
                    {"code": "ENG 101_LIT", "title": "A Survey of English Language", "units": 3, "semester": "first"},
                    {"code": "ENG 102_LIT", "title": "Introduction to English Grammar & Composition", "units": 2, "semester": "first"},
                    {"code": "ENG 103_LIT", "title": "Spoken English (Practical)", "units": 2, "semester": "first"},
                    {"code": "LIT 104", "title": "Introduction to Poetry", "units": 2, "semester": "first"},
                    {"code": "LIT 105", "title": "Introduction to Prose Literature", "units": 3, "semester": "first"},
                    {"code": "LIT 106", "title": "Introduction to Drama", "units": 3, "semester": "first"},
                    # Second Semester
                    {"code": "ENG 101_LIT_S2", "title": "A Survey of English Language", "units": 3, "semester": "second"},
                    {"code": "ENG 102_LIT_S2", "title": "Introduction to English Grammar & Composition", "units": 2, "semester": "second"},
                    {"code": "ENG 103_LIT_S2", "title": "Spoken English (Practical)", "units": 3, "semester": "second"},
                    {"code": "LIT 104_S2", "title": "Introduction to Poetry", "units": 3, "semester": "second"},
                    {"code": "LIT 105_S2", "title": "Introduction to Prose Literature", "units": 2, "semester": "second"},
                    {"code": "LIT 106_S2", "title": "Introduction to Drama", "units": 2, "semester": "second"},
                ],
                "200": [
                    {"code": "LIT 201", "title": "A Survey of the English Literature from Anglo Saxon to the Elizabethan Period.", "units": 2, "semester": "first"},
                    {"code": "LIT 202", "title": "Introduction to English Poetry", "units": 2, "semester": "first"},
                    {"code": "LIT 203", "title": "The English Novel from the 19th Century.", "units": 2, "semester": "first"},
                    {"code": "LIT 204", "title": "Literature, Popular Culture and the Mass Media.", "units": 2, "semester": "first"},
                    {"code": "LIT 205", "title": "Modern English Drama.", "units": 2, "semester": "first"},
                    {"code": "LIT 206", "title": "Introduction to Contemporary African Drama.", "units": 2, "semester": "first"},
                    {"code": "LIT 307_200", "title": "Entrepreneurial Literature", "units": 2, "semester": "first"},
                    {"code": "LIT 208", "title": "Prose Fiction", "units": 2, "semester": "first"},
                    {"code": "LIT 210", "title": "Creative Writing II", "units": 2, "semester": "first"},
                    # Second Semester (identical in text, using S2 variants)
                    {"code": "LIT 201_S2", "title": "A Survey of the English Literature from Anglo Saxon to the Elizabethan Period.", "units": 2, "semester": "second"},
                    {"code": "LIT 202_S2", "title": "Introduction to English Poetry.", "units": 2, "semester": "second"},
                    {"code": "LIT 203_S2", "title": "The English Novel from the 19th Century.", "units": 2, "semester": "second"},
                    {"code": "LIT 204_S2", "title": "Literature, Popular Culture and the Mass Media.", "units": 2, "semester": "second"},
                    {"code": "LIT 205_S2", "title": "Modern English Drama.", "units": 2, "semester": "second"},
                    {"code": "LIT 206_S2", "title": "Introduction to Contemporary African Drama.", "units": 2, "semester": "second"},
                    {"code": "LIT 307_200_S2", "title": "Entrepreneurial Literature", "units": 2, "semester": "second"},
                    {"code": "LIT 208_S2", "title": "Prose Fiction", "units": 2, "semester": "second"},
                    {"code": "LIT 210_S2", "title": "Creative Writing II", "units": 2, "semester": "second"},
                ],
                "300": [
                    {"code": "ENG 305_LIT", "title": "The English Language in Nigeria", "units": 2, "semester": "first"},
                    {"code": "LIT 301", "title": "Folklore in African Literature I.", "units": 2, "semester": "first"},
                    {"code": "LIT 302", "title": "Modern African Prose Fiction.", "units": 2, "semester": "first"},
                    {"code": "LIT 303", "title": "Modern African Poetry.", "units": 2, "semester": "first"},
                    {"code": "LIT 304", "title": "Modern African Drama.", "units": 2, "semester": "first"},
                    {"code": "LIT 306i", "title": "Nigerian Oral Literatures in English Translation", "units": 2, "semester": "first"},
                    {"code": "LIT 306_LIT", "title": "Discourse Analysis.", "units": 2, "semester": "first"},
                    {"code": "LIT 308_LIT", "title": "Creative Writing III", "units": 2, "semester": "first"},
                    {"code": "LIT 310", "title": "Introduction to Literary Criticism/Theories", "units": 2, "semester": "first"},
                    # Second Semester
                    {"code": "ENG 305_LIT_S2", "title": "The English Language in Nigeria", "units": 2, "semester": "second"},
                    {"code": "LIT 301_S2", "title": "Folklore in African Literature I.", "units": 2, "semester": "second"},
                    {"code": "LIT 302_S2", "title": "Modern African Prose Fiction.", "units": 2, "semester": "second"},
                    {"code": "LIT 303_S2", "title": "Modern African Poetry.", "units": 2, "semester": "second"},
                    {"code": "LIT 304_S2", "title": "Modern African Drama.", "units": 2, "semester": "second"},
                    {"code": "LIT 306i_S2", "title": "Nigerian Oral Literatures in English Translation", "units": 2, "semester": "second"},
                    {"code": "LIT 306_LIT_S2", "title": "Discourse Analysis.", "units": 2, "semester": "second"},
                    {"code": "LIT 308_LIT_S2", "title": "Creative Writing III", "units": 2, "semester": "second"},
                    {"code": "LIT 310_S2", "title": "Introduction to Literary Criticism/Theories", "units": 2, "semester": "second"},
                ],
                "400": [
                    {"code": "LIT 401", "title": "Advance Literary Theory and Criticism.", "units": 2, "semester": "first"},
                    {"code": "LIT 402", "title": "Commonwealth Literature.", "units": 2, "semester": "first"},
                    {"code": "LIT 403", "title": "African-American and Caribbean Literature.", "units": 2, "semester": "first"},
                    {"code": "LIT 421", "title": "Stylistics", "units": 2, "semester": "first"},
                    {"code": "LIT 423", "title": "Research Methods", "units": 2, "semester": "first"},
                    {"code": "LIT 424", "title": "Project", "units": 6, "semester": "first"},
                    # Second Semester (repeated in text)
                    {"code": "LIT 401_S2", "title": "Advance Literary Theory and Criticism.", "units": 2, "semester": "second"},
                    {"code": "LIT 402_S2", "title": "Commonwealth Literature.", "units": 2, "semester": "second"},
                    {"code": "LIT 403_S2", "title": "African-American and Caribbean Literature.", "units": 2, "semester": "second"},
                    {"code": "LIT 421_S2", "title": "Stylistics", "units": 2, "semester": "second"},
                    {"code": "LIT 423_S2", "title": "Research Methods", "units": 2, "semester": "second"},
                    {"code": "LIT 424_S2", "title": "Project", "units": 6, "semester": "second"},
                ]
            })
        ]

        # 4. Helper to resolve cross-programme/cross-dept code collisions
        def get_safe_code(original_code, target_programme, target_dept_name):
            existing = Course.objects.filter(code=original_code).first()
            if not existing: return original_code

            # Collision with different programme
            is_cross_programme = False
            for offering in existing.offerings.all():
                if offering.department.faculty.programme_type != target_programme:
                    is_cross_programme = True
                    break
            
            if is_cross_programme:
                return f"{original_code}_DEG"
            
            return original_code

        # 5. Process Curricula
        for dept, levels_data in curricula:
            self.stdout.write(self.style.SUCCESS(f"\n>>> DEPARTMENT: {dept.name} <<<"))
            
            for level_name, courses in levels_data.items():
                level = Level.objects.filter(name=level_name).first()
                if not level:
                    self.stdout.write(self.style.ERROR(f"Level '{level_name}' not found!"))
                    continue

                self.stdout.write(self.style.NOTICE(f"--- Level: {level.display_name} ---"))

                for c in courses:
                    original_code = c["code"]
                    # If current level/dept already has an entry for this code, skip or update?
                    # Suffix handling
                    special_suffixes = ["_LIT", "_ENG", "_S2", "_alt", "_200", "_alt1"]
                    clean_code = original_code
                    for s in special_suffixes:
                        if s in clean_code: clean_code = clean_code.replace(s, "")
                    
                    safe_code = get_safe_code(clean_code, faculty.programme_type, dept.name)
                    
                    # If we used a suffix in the data dict, it might be intentional for the same programme
                    if "_" in original_code and original_code != safe_code:
                        final_code = original_code
                    else:
                        final_code = safe_code

                    if dry_run:
                        self.stdout.write(f"[DRY-RUN] Process {final_code}: {c['title']} ({c['units']} Units)")
                        continue

                    # I. Course Record (Idempotent)
                    course, created = Course.objects.update_or_create(
                        code=final_code,
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
                        self.stdout.write(f"   Link already exists for {course.code}")

        if not dry_run:
            self.stdout.write(self.style.SUCCESS("\nSuccessfully processed Arts curriculum."))
