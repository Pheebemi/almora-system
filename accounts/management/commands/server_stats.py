from django.core.management.base import BaseCommand
from accounts.models import (
    User, StudentProfile, StaffProfile, Faculty, Department,
    Course, CourseOffering, CourseRegistration, AcademicRecord,
    PaymentTransaction, AcademicSession
)


class Command(BaseCommand):
    help = "Show live server data statistics"

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("\n========== LIVE SERVER STATS ==========\n"))

        # Users
        total_users = User.objects.count()
        students = User.objects.filter(user_type='student').count()
        staff = User.objects.filter(user_type='staff').count()
        verified = User.objects.filter(is_verified=True).count()
        self.stdout.write(self.style.SUCCESS("--- Users ---"))
        self.stdout.write(f"  Total Users        : {total_users}")
        self.stdout.write(f"  Students           : {students}")
        self.stdout.write(f"  Staff              : {staff}")
        self.stdout.write(f"  Verified           : {verified}")

        # Profiles
        student_profiles = StudentProfile.objects.count()
        staff_profiles = StaffProfile.objects.count()
        self.stdout.write(self.style.SUCCESS("\n--- Profiles ---"))
        self.stdout.write(f"  Student Profiles   : {student_profiles}")
        self.stdout.write(f"  Staff Profiles     : {staff_profiles}")
        self.stdout.write(f"  Missing (students) : {students - student_profiles}")

        # Academic Structure
        faculties = Faculty.objects.count()
        departments = Department.objects.count()
        sessions = AcademicSession.objects.count()
        active_session = AcademicSession.objects.filter(is_active=True).first()
        self.stdout.write(self.style.SUCCESS("\n--- Academic Structure ---"))
        self.stdout.write(f"  Faculties          : {faculties}")
        self.stdout.write(f"  Departments        : {departments}")
        self.stdout.write(f"  Academic Sessions  : {sessions}")
        self.stdout.write(f"  Active Session     : {active_session or 'NONE'}")

        # Courses
        total_courses = Course.objects.count()
        active_courses = Course.objects.filter(is_active=True).count()
        offerings = CourseOffering.objects.count()
        self.stdout.write(self.style.SUCCESS("\n--- Courses ---"))
        self.stdout.write(f"  Total Courses      : {total_courses}")
        self.stdout.write(f"  Active Courses     : {active_courses}")
        self.stdout.write(f"  Course Offerings   : {offerings}")

        # Activity
        registrations = CourseRegistration.objects.count()
        academic_records = AcademicRecord.objects.count()
        payments = PaymentTransaction.objects.count()
        self.stdout.write(self.style.SUCCESS("\n--- Activity ---"))
        self.stdout.write(f"  Course Registrations : {registrations}")
        self.stdout.write(f"  Academic Records     : {academic_records}")
        self.stdout.write(f"  Payment Transactions : {payments}")

        # Per department student count
        self.stdout.write(self.style.SUCCESS("\n--- Students per Department ---"))
        for dept in Department.objects.all():
            count = StudentProfile.objects.filter(department=dept).count()
            if count > 0:
                self.stdout.write(f"  {dept.name:<35}: {count}")

        self.stdout.write(self.style.MIGRATE_HEADING("\n========================================\n"))
