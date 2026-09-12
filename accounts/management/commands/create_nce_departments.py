from django.core.management.base import BaseCommand
from accounts.models import Faculty, Department

class Command(BaseCommand):
    help = "Create new NCE departments under the NCE Education faculty"

    # (name, short_name)
    DEPARTMENTS = [
        ("NCE Political Science and Christian Religious Studies", "NCPC"),
        ("NCE Social Studies and Christian Religious Studies", "NCSC"),
    ]

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

        faculty = Faculty.objects.filter(
            name="NCE Education", programme_type="nce"
        ).first()
        if not faculty:
            self.stdout.write(self.style.ERROR("NCE Education (NCE) not found!"))
            return

        self.stdout.write(f"Targeting Faculty: {faculty.name} ({faculty.programme_type})")

        for name, short_name in self.DEPARTMENTS:
            existing = Department.objects.filter(faculty=faculty, name=name).first()
            if existing:
                self.stdout.write(
                    f"Already exists: {existing.name} ({existing.short_name}) - skipped"
                )
                continue

            # Guard against a differently-named record already holding this code
            clash = Department.objects.filter(faculty=faculty, short_name=short_name).first()
            if clash:
                self.stdout.write(self.style.ERROR(
                    f"Short name '{short_name}' is already used by '{clash.name}' - skipped"
                ))
                continue

            if dry_run:
                self.stdout.write(f"[DRY-RUN] Would create: {name} ({short_name})")
                continue

            dept = Department.objects.create(
                name=name,
                faculty=faculty,
                short_name=short_name,
            )
            self.stdout.write(self.style.SUCCESS(f"Created: {dept.name} ({dept.short_name})"))

        if not dry_run:
            self.stdout.write(self.style.SUCCESS("\nDone."))
