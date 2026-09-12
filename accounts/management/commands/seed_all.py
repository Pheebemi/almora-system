"""
Seed ALL data for a fresh deployment: academic session, levels, programmes,
departments, staff, students, courses, course offerings, fee structures,
and program choices.

Run: python manage.py seed_all
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import (
    Faculty, Department, StaffProfile, StudentProfile,
    Level, AcademicSession, FeeStructure,
    Course, CourseOffering, CourseRegistration,
)
from core.models import Program, ProgramChoice
from datetime import date, timedelta

User = get_user_model()

DEFAULT_PASSWORD = "almora123"


class Command(BaseCommand):
    help = "Seed all data for a fresh deployment (idempotent - safe to run again)"

    def add_arguments(self, parser):
        parser.add_argument(
            "--password", type=str, default=DEFAULT_PASSWORD,
            help=f"Password for seeded users (default: {DEFAULT_PASSWORD})",
        )

    def handle(self, *args, **options):
        password = options["password"]
        self.stdout.write(self.style.MIGRATE_HEADING("\n=== Seeding Almora Polytechnic Pantisawa Data ===\n"))

        session = self._create_academic_session()
        self._create_levels()
        faculties = self._create_faculties_and_departments()
        self._create_staff(faculties, password)
        self._create_students(faculties, session, password)
        self._create_courses(faculties, session)
        self._create_fee_structures(session)
        self._create_programs_and_choices()

        self.stdout.write(self.style.SUCCESS("\n=== All data seeded successfully! ==="))
        self.stdout.write(self.style.WARNING(f"Default password for all users: {password}"))
        self.stdout.write("Change passwords after first login.\n")

    # ------------------------------------------------------------------ #
    # Academic Session
    # ------------------------------------------------------------------ #
    def _create_academic_session(self):
        self.stdout.write(self.style.MIGRATE_HEADING("1. Academic Session"))
        session, created = AcademicSession.objects.get_or_create(
            name="2024/2025",
            defaults={
                "start_year": 2024,
                "end_year": 2025,
                "session_type": "regular",
                "is_active": True,
                "start_date": date(2024, 9, 1),
                "end_date": date(2025, 8, 31),
                "registration_deadline": date(2024, 10, 15),
            },
        )
        status = "Created" if created else "Already exists"
        self.stdout.write(f"   {status}: {session.name} (active={session.is_active})")
        return session

    # ------------------------------------------------------------------ #
    # Levels
    # ------------------------------------------------------------------ #
    def _create_levels(self):
        self.stdout.write(self.style.MIGRATE_HEADING("2. Levels"))
        levels_data = [
            # Degree
            ("100", "100 Level", 1, "degree"),
            ("200", "200 Level", 2, "degree"),
            ("300", "300 Level", 3, "degree"),
            ("400", "400 Level", 4, "degree"),
            # ND
            ("ND1", "ND 1", 5, "nd"),
            ("ND2", "ND 2", 6, "nd"),
            # NCE
            ("NCE1", "NCE 1", 7, "nce"),
            ("NCE2", "NCE 2", 8, "nce"),
        ]
        for name, display, order, prog in levels_data:
            lvl, created = Level.objects.get_or_create(
                name=name,
                defaults={"display_name": display, "order": order, "programme_type": prog, "is_active": True},
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f"   Created: {display} ({prog})"))

    # ------------------------------------------------------------------ #
    # Faculties & Departments
    # ------------------------------------------------------------------ #
    def _create_faculties_and_departments(self):
        self.stdout.write(self.style.MIGRATE_HEADING("3. Faculties & Departments"))
        data = {
            "degree": [
                {
                    "faculty": {"name": "Faculty of Science", "short_name": "FOS"},
                    "departments": [
                        {"name": "Computer Science", "short_name": "CSC"},
                        {"name": "Mathematics", "short_name": "MTH"},
                        {"name": "Statistics", "short_name": "STA"},
                    ],
                },
                {
                    "faculty": {"name": "Faculty of Social Sciences", "short_name": "FOSS"},
                    "departments": [
                        {"name": "Political Science", "short_name": "POL"},
                        {"name": "Sociology", "short_name": "SOC"},
                        {"name": "Economics", "short_name": "ECO"},
                    ],
                },
                {
                    "faculty": {"name": "Faculty of Management Sciences", "short_name": "FOMS"},
                    "departments": [
                        {"name": "Business Administration", "short_name": "BUS"},
                        {"name": "Public Administration", "short_name": "PUB"},
                        {"name": "Accounting", "short_name": "ACC"},
                    ],
                },
                {
                    "faculty": {"name": "Faculty of Arts", "short_name": "FOA"},
                    "departments": [
                        {"name": "English and Literary Studies", "short_name": "ENG"},
                        {"name": "Christian Religious Studies", "short_name": "CRS"},
                        {"name": "Islamic Religious Studies", "short_name": "IRS"},
                    ],
                },
                {
                    "faculty": {"name": "Faculty of Education", "short_name": "FOE"},
                    "departments": [
                        {"name": "Health Education", "short_name": "HED"},
                        {"name": "Physical Education", "short_name": "PED"},
                        {"name": "Biology Education", "short_name": "BED"},
                    ],
                },
            ],
            "nd": [
                {
                    "faculty": {"name": "School of Diploma Studies", "short_name": "SDS"},
                    "departments": [
                        {"name": "Diploma Computer Science", "short_name": "DCS"},
                        {"name": "Diploma Public Health", "short_name": "DPH"},
                    ],
                },
            ],
            "nce": [
                {
                    "faculty": {"name": "School of NCE Education", "short_name": "SNE"},
                    "departments": [
                        {"name": "NCE Economics", "short_name": "NECO"},
                        {"name": "NCE Political Science", "short_name": "NCPS"},
                        {"name": "NCE Arabic", "short_name": "NCAR"},
                        {"name": "NCE Islamic Studies", "short_name": "NCIS"},
                        {"name": "NCE English", "short_name": "NCEN"},
                        {"name": "NCE History", "short_name": "NCHI"},
                        {"name": "NCE Fulfulde", "short_name": "NCFU"},
                        {"name": "NCE Mumuve Language", "short_name": "NCMU"},
                        {"name": "NCE Christian Religious Studies", "short_name": "NCCR"},
                        {"name": "NCE Hausa", "short_name": "NCHA"},
                        {"name": "NCE Business Education", "short_name": "NCBE"},
                    ],
                },
            ],
        }

        faculties = {}
        for prog_type, faculty_list in data.items():
            for fac_data in faculty_list:
                fac, created = Faculty.objects.get_or_create(
                    programme_type=prog_type,
                    short_name=fac_data["faculty"]["short_name"],
                    defaults={"name": fac_data["faculty"]["name"]},
                )
                if created:
                    self.stdout.write(self.style.SUCCESS(f"   Faculty: {fac.name} ({prog_type})"))

                depts = []
                for dept_data in fac_data["departments"]:
                    dept, d_created = Department.objects.get_or_create(
                        faculty=fac,
                        short_name=dept_data["short_name"],
                        defaults={"name": dept_data["name"]},
                    )
                    depts.append(dept)
                    if d_created:
                        self.stdout.write(f"     Dept: {dept.name}")

                faculties.setdefault(prog_type, []).append({"faculty": fac, "departments": depts})

        return faculties

    # ------------------------------------------------------------------ #
    # Staff
    # ------------------------------------------------------------------ #
    def _create_staff(self, faculties, password):
        self.stdout.write(self.style.MIGRATE_HEADING("4. Staff"))
        staff_data = {
            "degree": [
                {"username": "degree_staff1", "first_name": "John", "last_name": "Okoro", "email": "john.okoro@almorapoly.edu.ng"},
                {"username": "degree_staff2", "first_name": "Amina", "last_name": "Bello", "email": "amina.bello@almorapoly.edu.ng"},
                {"username": "degree_staff3", "first_name": "Chukwu", "last_name": "Eze", "email": "chukwu.eze@almorapoly.edu.ng"},
            ],
            "nd": [
                {"username": "nd_staff1", "first_name": "Ibrahim", "last_name": "Yusuf", "email": "ibrahim.yusuf@almorapoly.edu.ng"},
                {"username": "nd_staff2", "first_name": "Fatima", "last_name": "Hassan", "email": "fatima.hassan@almorapoly.edu.ng"},
            ],
            "nce": [
                {"username": "nce_staff1", "first_name": "Grace", "last_name": "Eze", "email": "grace.eze@almorapoly.edu.ng"},
                {"username": "nce_staff2", "first_name": "Chidi", "last_name": "Nwosu", "email": "chidi.nwosu@almorapoly.edu.ng"},
            ],
        }

        for prog_type, staff_list in staff_data.items():
            fac_list = faculties.get(prog_type, [])
            if not fac_list:
                continue
            fac = fac_list[0]["faculty"]
            dept = fac_list[0]["departments"][0] if fac_list[0]["departments"] else None
            if not dept:
                continue

            for i, s in enumerate(staff_list):
                # Rotate departments
                dept = fac_list[0]["departments"][i % len(fac_list[0]["departments"])]
                user, created = User.objects.get_or_create(
                    username=s["username"],
                    defaults={
                        "user_type": "staff",
                        "is_verified": True,
                        "is_staff": True,
                        "first_name": s["first_name"],
                        "last_name": s["last_name"],
                        "email": s["email"],
                    },
                )
                if created:
                    user.set_password(password)
                    user.save()
                    profile, _ = StaffProfile.objects.get_or_create(
                        user=user,
                        defaults={
                            "staff_id": f"SF-{s['username'].upper()}",
                            "staff_type": "academic",
                            "faculty": fac,
                            "department": dept,
                            "qualification": "M.Sc" if i == 0 else "B.Sc",
                        },
                    )
                    self.stdout.write(self.style.SUCCESS(
                        f"   Staff: {s['username']} -> {fac.name} / {dept.name}"
                    ))

    # ------------------------------------------------------------------ #
    # Students
    # ------------------------------------------------------------------ #
    def _create_students(self, faculties, session, password):
        self.stdout.write(self.style.MIGRATE_HEADING("5. Students"))
        student_data = {
            "degree": [
                {"username": "STU001", "matric": "LVC/DEG/2024/001", "first_name": "Aisha", "last_name": "Mohammed", "gender": "F", "level": "100", "program": "BSc"},
                {"username": "STU002", "matric": "LVC/DEG/2024/002", "first_name": "Emeka", "last_name": "Obi", "gender": "M", "level": "200", "program": "BSc"},
                {"username": "STU003", "matric": "LVC/DEG/2024/003", "first_name": "Blessing", "last_name": "Adeyemi", "gender": "F", "level": "100", "program": "BEd"},
                {"username": "STU004", "matric": "LVC/DEG/2024/004", "first_name": "David", "last_name": "Okonkwo", "gender": "M", "level": "300", "program": "BSc"},
            ],
            "nd": [
                {"username": "STU005", "matric": "LVC/ND/2024/001", "first_name": "Yusuf", "last_name": "Abdullahi", "gender": "M", "level": "ND1", "program": "BTech"},
                {"username": "STU006", "matric": "LVC/ND/2024/002", "first_name": "Halima", "last_name": "Bala", "gender": "F", "level": "ND2", "program": "BTech"},
            ],
            "nce": [
                {"username": "STU007", "matric": "LVC/NCE/2024/001", "first_name": "Chioma", "last_name": "Nwankwo", "gender": "F", "level": "NCE1", "program": "BEd"},
                {"username": "STU008", "matric": "LVC/NCE/2024/002", "first_name": "Musa", "last_name": "Garba", "gender": "M", "level": "NCE2", "program": "BEd"},
            ],
        }

        states = ["Taraba", "Adamawa", "Borno", "Plateau", "Nasarawa", "Lagos", "Kaduna", "Benue"]

        for prog_type, students in student_data.items():
            fac_list = faculties.get(prog_type, [])
            if not fac_list:
                continue
            fac = fac_list[0]["faculty"]
            depts = fac_list[0]["departments"]

            for i, s in enumerate(students):
                dept = depts[i % len(depts)]
                level = Level.objects.filter(name=s["level"]).first()
                if not level:
                    continue

                user, created = User.objects.get_or_create(
                    username=s["username"],
                    defaults={
                        "user_type": "student",
                        "is_verified": True,
                        "first_name": s["first_name"],
                        "last_name": s["last_name"],
                        "matriculation_number": s["matric"],
                        "email": f"{s['username'].lower()}@students.almorapoly.edu.ng",
                    },
                )
                if created:
                    user.set_password(password)
                    user.save()
                    state = states[i % len(states)]
                    # Signal may have created a default profile; update it or create
                    profile, p_created = StudentProfile.objects.get_or_create(user=user)
                    profile.programme_type = prog_type
                    profile.gender = s["gender"]
                    profile.faculty = fac
                    profile.department = dept
                    profile.program = s["program"]
                    profile.admission_year = "2024"
                    profile.current_level = level
                    profile.current_semester = "first"
                    profile.current_session = session
                    profile.state_of_origin = state
                    profile.local_government = f"{state} Central"
                    profile.date_of_birth = date(2000 + i, 3, 15)
                    profile.save()
                    self.stdout.write(self.style.SUCCESS(
                        f"   Student: {s['matric']} ({s['first_name']} {s['last_name']}) -> {dept.name} / {level.display_name}"
                    ))

    # ------------------------------------------------------------------ #
    # Courses & Offerings
    # ------------------------------------------------------------------ #
    def _create_courses(self, faculties, session):
        self.stdout.write(self.style.MIGRATE_HEADING("6. Courses & Offerings"))
        courses_data = {
            "degree": [
                # 100 Level
                {"code": "CSC101", "title": "Introduction to Computer Science", "credits": 3, "semester": "first", "levels": ["100"]},
                {"code": "CSC102", "title": "Introduction to Programming", "credits": 3, "semester": "second", "levels": ["100"]},
                {"code": "MTH101", "title": "Elementary Mathematics I", "credits": 3, "semester": "first", "levels": ["100"]},
                {"code": "MTH102", "title": "Elementary Mathematics II", "credits": 3, "semester": "second", "levels": ["100"]},
                {"code": "PHY101", "title": "General Physics I", "credits": 3, "semester": "first", "levels": ["100"]},
                {"code": "PHY102", "title": "General Physics II", "credits": 3, "semester": "second", "levels": ["100"]},
                {"code": "GST101", "title": "Use of English I", "credits": 2, "semester": "first", "levels": ["100"]},
                {"code": "GST102", "title": "Use of English II", "credits": 2, "semester": "second", "levels": ["100"]},
                # 200 Level
                {"code": "CSC201", "title": "Data Structures", "credits": 3, "semester": "first", "levels": ["200"]},
                {"code": "CSC202", "title": "Computer Architecture", "credits": 3, "semester": "second", "levels": ["200"]},
                {"code": "MTH201", "title": "Mathematical Methods I", "credits": 3, "semester": "first", "levels": ["200"]},
                {"code": "MTH202", "title": "Linear Algebra", "credits": 3, "semester": "second", "levels": ["200"]},
                # 300 Level
                {"code": "CSC301", "title": "Operating Systems", "credits": 3, "semester": "first", "levels": ["300"]},
                {"code": "CSC302", "title": "Database Management Systems", "credits": 3, "semester": "second", "levels": ["300"]},
                {"code": "EDU301", "title": "Philosophy of Education", "credits": 2, "semester": "first", "levels": ["300"]},
                # 400 Level
                {"code": "CSC401", "title": "Software Engineering", "credits": 3, "semester": "first", "levels": ["400"]},
                {"code": "CSC402", "title": "Final Year Project", "credits": 6, "semester": "second", "levels": ["400"]},
            ],
            "nd": [
                {"code": "NDC101", "title": "ND Introduction to Computing", "credits": 3, "semester": "first", "levels": ["ND1"]},
                {"code": "NDC102", "title": "ND Programming Fundamentals", "credits": 3, "semester": "second", "levels": ["ND1"]},
                {"code": "NDE101", "title": "ND Engineering Drawing", "credits": 2, "semester": "first", "levels": ["ND1"]},
                {"code": "NDE102", "title": "ND Workshop Practice", "credits": 2, "semester": "second", "levels": ["ND1"]},
                {"code": "NDC201", "title": "ND Database Systems", "credits": 3, "semester": "first", "levels": ["ND2"]},
                {"code": "NDC202", "title": "ND Project", "credits": 4, "semester": "second", "levels": ["ND2"]},
            ],
            "nce": [
                {"code": "NCE101", "title": "NCE Foundation of Education", "credits": 2, "semester": "first", "levels": ["NCE1"]},
                {"code": "NCE102", "title": "NCE Educational Psychology", "credits": 2, "semester": "second", "levels": ["NCE1"]},
                {"code": "NCE103", "title": "NCE Primary Science Methods", "credits": 3, "semester": "first", "levels": ["NCE1"]},
                {"code": "NCE104", "title": "NCE English Methods", "credits": 3, "semester": "second", "levels": ["NCE1"]},
                {"code": "NCE201", "title": "NCE Teaching Practice", "credits": 4, "semester": "first", "levels": ["NCE2"]},
                {"code": "NCE202", "title": "NCE Project", "credits": 4, "semester": "second", "levels": ["NCE2"]},
            ],
        }

        staff_user = User.objects.filter(user_type="staff").first()

        for prog_type, course_list in courses_data.items():
            fac_list = faculties.get(prog_type, [])
            if not fac_list:
                continue
            depts = fac_list[0]["departments"]

            for c in course_list:
                course, created = Course.objects.get_or_create(
                    code=c["code"],
                    defaults={
                        "title": c["title"],
                        "credits": c["credits"],
                        "semester": c["semester"],
                        "academic_session": session,
                        "created_by": staff_user,
                    },
                )
                if created:
                    self.stdout.write(f"   Course: {c['code']} - {c['title']}")

                # Create offerings for each dept and level
                for level_name in c["levels"]:
                    level = Level.objects.filter(name=level_name).first()
                    if not level:
                        continue
                    for dept in depts:
                        CourseOffering.objects.get_or_create(
                            course=course,
                            department=dept,
                            level=level,
                            defaults={"is_active": True},
                        )

    # ------------------------------------------------------------------ #
    # Fee Structures
    # ------------------------------------------------------------------ #
    def _create_fee_structures(self, session):
        self.stdout.write(self.style.MIGRATE_HEADING("7. Fee Structures"))
        
        created = 0
        for dept in Department.objects.select_related("faculty").all():
            prog_type = getattr(dept.faculty, "programme_type", "degree") or "degree"
            
            # Determine fee amount based on faculty and programme type
            if prog_type == "degree":
                # Science faculty: 65,000 per level
                # Other degree faculties: 60,000 per level
                is_science = dept.faculty.short_name == "FOS"  # Faculty of Science
                fee_amount = 65000 if is_science else 60000
                fee_amounts = {
                    "100": fee_amount,
                    "200": fee_amount,
                    "300": fee_amount,
                    "400": fee_amount,
                }
            elif prog_type == "nd":
                fee_amounts = {"ND1": 38000, "ND2": 38000}
            else:  # nce
                fee_amounts = {"NCE1": 40000, "NCE2": 40000}
            
            for level in Level.objects.filter(programme_type=prog_type, is_active=True):
                if level.name not in fee_amounts:
                    continue
                _, c = FeeStructure.objects.get_or_create(
                    academic_session=session,
                    department=dept,
                    level=level,
                    defaults={"amount": fee_amounts[level.name]},
                )
                if c:
                    created += 1

        # Applicant / Screening fees (unchanged - leaving applicant part intact)
        admin_fac, _ = Faculty.objects.get_or_create(
            short_name="ADMIN", programme_type="degree",
            defaults={"name": "Central Administration"},
        )
        scr_dept, _ = Department.objects.get_or_create(
            faculty=admin_fac, short_name="SCREENING",
            defaults={"name": "Screening"},
        )
        applicant_fees = [
            ("APP_DEG", "Applicant (Degree)", "degree", 90, 12000),
            ("APP_ND", "Applicant (ND)", "nd", 91, 5000),
            ("APP_NCE", "Applicant (NCE)", "nce", 92, 5000),
        ]
        for name, display, prog, order, amount in applicant_fees:
            lvl, _ = Level.objects.get_or_create(
                name=name,
                defaults={"display_name": display, "programme_type": prog, "order": order, "is_active": True},
            )
            _, c = FeeStructure.objects.get_or_create(
                academic_session=session, department=scr_dept, level=lvl,
                defaults={"amount": amount},
            )
            if c:
                created += 1

        self.stdout.write(f"   Fee structures created: {created}")

    # ------------------------------------------------------------------ #
    # Programs & Program Choices (for applicants)
    # ------------------------------------------------------------------ #
    def _create_programs_and_choices(self):
        self.stdout.write(self.style.MIGRATE_HEADING("8. Programs & Choices (Applicants)"))

        programs = [
            ("NCE Programme", "nce"),
            ("ND (Diploma) Programme", "diploma"),
            ("Degree Programme", "degree"),
        ]
        for name, ptype in programs:
            Program.objects.get_or_create(
                name=name, program_type=ptype,
                defaults={"description": f"{name} at Almora Polytechnic Pantisawa"},
            )

        choices = {
            "diploma": ["Computer Science", "Public Health"],
            "degree": [
                # Faculty of Science (65k)
                "BSc Computer Science", "BSc Mathematics", "BSc Statistics",
                # Faculty of Social Sciences (60k)
                "BSc Political Science", "BSc Sociology", "BSc Economics",
                # Faculty of Management Sciences (60k)
                "BSc Business Administration", "BSc Public Administration", "BSc Accounting",
                # Faculty of Arts (60k)
                "BA English and Literary Studies", "BA Christian Religious Studies", "BA Islamic Religious Studies",
                # Faculty of Education (60k)
                "BSc (Ed) Health Education", "BSc (Ed) Physical Education", "BSc (Ed) Biology Education",
            ],
            "nce": [
                "NCE Economics", "NCE Political Science", "NCE Arabic",
                "NCE Islamic Studies", "NCE English", "NCE History",
                "NCE Fulfulde", "NCE Mumuve Language", "NCE Christian Religious Studies",
                "NCE Hausa", "NCE Business Education",
            ],
        }
        for ptype, names in choices.items():
            for name in names:
                ProgramChoice.objects.get_or_create(
                    program_type=ptype, name=name,
                    defaults={"description": f"{name} - {ptype.upper()} Program"},
                )
        self.stdout.write("   Programs and choices created.")
