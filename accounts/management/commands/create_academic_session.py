from django.core.management.base import BaseCommand
from accounts.models import AcademicSession
from datetime import date, timedelta


class Command(BaseCommand):
    help = 'Create a new academic session'

    def add_arguments(self, parser):
        parser.add_argument(
            'session_name',
            type=str,
            help='Name of the academic session (e.g., "2024/2025")'
        )
        parser.add_argument(
            '--start-date',
            type=str,
            help='Start date in YYYY-MM-DD format (default: September 1 of start year)'
        )
        parser.add_argument(
            '--end-date',
            type=str,
            help='End date in YYYY-MM-DD format (default: August 31 of end year)'
        )
        parser.add_argument(
            '--registration-deadline',
            type=str,
            help='Registration deadline in YYYY-MM-DD format (default: 2 weeks after start)'
        )
        parser.add_argument(
            '--session-type',
            type=str,
            choices=['regular', 'special'],
            default='regular',
            help='Type of session (default: regular)'
        )
        parser.add_argument(
            '--activate',
            action='store_true',
            help='Set this session as active (will deactivate other sessions)'
        )

    def handle(self, *args, **options):
        session_name = options['session_name']

        # Parse session name to get years
        try:
            start_year, end_year = map(int, session_name.split('/'))
        except ValueError:
            self.stderr.write("Invalid session name format. Use format like '2024/2025'")
            return

        # Set default dates if not provided
        start_date = options.get('start_date')
        if not start_date:
            start_date = date(start_year, 9, 1)  # September 1st
        else:
            start_date = date.fromisoformat(start_date)

        end_date = options.get('end_date')
        if not end_date:
            end_date = date(end_year, 8, 31)  # August 31st
        else:
            end_date = date.fromisoformat(end_date)

        registration_deadline = options.get('registration_deadline')
        if not registration_deadline:
            registration_deadline = start_date + timedelta(weeks=2)  # 2 weeks after start
        else:
            registration_deadline = date.fromisoformat(registration_deadline)

        session_type = options['session_type']
        is_active = options['activate']

        # Check if session already exists
        if AcademicSession.objects.filter(name=session_name).exists():
            self.stderr.write(f"Academic session '{session_name}' already exists")
            return

        # Create the session
        session = AcademicSession.objects.create(
            name=session_name,
            start_year=start_year,
            end_year=end_year,
            session_type=session_type,
            is_active=is_active,
            start_date=start_date,
            end_date=end_date,
            registration_deadline=registration_deadline
        )

        self.stdout.write(
            self.style.SUCCESS(f"Created academic session: {session.name}")
        )
        self.stdout.write(f"  Type: {session.session_type}")
        self.stdout.write(f"  Active: {session.is_active}")
        self.stdout.write(f"  Start: {session.start_date}")
        self.stdout.write(f"  End: {session.end_date}")
        self.stdout.write(f"  Registration deadline: {session.registration_deadline}")

        if is_active:
            self.stdout.write("  Note: This session is now active. Other sessions have been deactivated.")