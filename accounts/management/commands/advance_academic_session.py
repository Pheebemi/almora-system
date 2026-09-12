from django.core.management.base import BaseCommand
from accounts.models import StudentProfile, Level, AcademicSession
from datetime import date


class Command(BaseCommand):
    help = 'Advance students to the next academic session and level/semester'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without actually making changes',
        )
        parser.add_argument(
            '--session-name',
            type=str,
            help='Specific session name to advance to (optional - will use active session)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        # Get the target session
        if options['session_name']:
            try:
                target_session = AcademicSession.objects.get(name=options['session_name'])
            except AcademicSession.DoesNotExist:
                self.stderr.write(f"Session '{options['session_name']}' not found")
                return
        else:
            target_session = AcademicSession.objects.filter(is_active=True).first()
            if not target_session:
                self.stderr.write("No active academic session found")
                return

        self.stdout.write(f"Advancing students to session: {target_session.name}")
        if dry_run:
            self.stdout.write("DRY RUN - No changes will be made")

        # Get all students
        students = StudentProfile.objects.select_related('current_level').all()
        advanced_count = 0
        semester_advanced_count = 0
        level_advanced_count = 0

        for student in students:
            original_level = student.current_level.name
            original_semester = student.current_semester

            # Advance semester first
            if student.current_semester == 'first':
                student.current_semester = 'second'
                semester_advanced_count += 1
                if not dry_run:
                    student.save()
                self.stdout.write(f"  {student.user.get_full_name()}: {original_semester} → {student.current_semester}")
            else:
                # End of year - advance to next level
                next_level = Level.objects.filter(order=student.current_level.order + 1).first()
                if next_level:
                    student.current_level = next_level
                    student.current_semester = 'first'  # Start new level with first semester
                    level_advanced_count += 1
                    if not dry_run:
                        student.save()
                    self.stdout.write(f"  {student.user.get_full_name()}: Level {original_level} → Level {next_level.name}, Semester {original_semester} → first")
                else:
                    self.stdout.write(f"  {student.user.get_full_name()}: Already at final level ({original_level}), cannot advance further")

            # Update current session
            if student.current_session != target_session:
                student.current_session = target_session
                if not dry_run:
                    student.save()

        # Summary
        self.stdout.write("\nSummary:")
        self.stdout.write(f"  Students advanced to next semester: {semester_advanced_count}")
        self.stdout.write(f"  Students advanced to next level: {level_advanced_count}")
        self.stdout.write(f"  Total students processed: {students.count()}")

        if dry_run:
            self.stdout.write("\nThis was a dry run. Run without --dry-run to apply changes.")