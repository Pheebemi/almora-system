from collections import Counter

from django.core.management.base import BaseCommand
from django.db import transaction

from accounts.models import StudentProfile, Level, AcademicSession


class Command(BaseCommand):
    help = (
        "Promote students one level within their own programme and move them "
        "to the target academic session. Applicants are excluded."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would change without writing anything',
        )
        parser.add_argument(
            '--session-name',
            type=str,
            help='Session to move students into (defaults to the active session)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        if dry_run:
            self.stdout.write(self.style.WARNING("DRY RUN MODE - No changes will be saved."))

        # 1. Resolve target session
        if options['session_name']:
            target_session = AcademicSession.objects.filter(name=options['session_name']).first()
            if not target_session:
                self.stderr.write(f"Session '{options['session_name']}' not found")
                return
        else:
            target_session = AcademicSession.objects.filter(is_active=True).first()
            if not target_session:
                self.stderr.write("No active academic session found")
                return

        self.stdout.write(f"Target session: {target_session.name}")

        # 2. Build the level -> next level map once, per programme.
        #    Next level is the nearest higher `order` *within the same programme*,
        #    so ND2 can never roll into NCE1. Applicant levels are not promotable.
        real_levels = Level.objects.exclude(name__startswith='APP_').order_by('order')
        next_level_for = {}
        for lvl in real_levels:
            next_level_for[lvl.pk] = (
                real_levels
                .filter(programme_type=lvl.programme_type, order__gt=lvl.order)
                .first()
            )

        self.stdout.write("\nPromotion map:")
        for lvl in real_levels:
            nxt = next_level_for[lvl.pk]
            arrow = nxt.name if nxt else "(final level)"
            self.stdout.write(f"  {lvl.programme_type:<7} {lvl.name:<8} -> {arrow}")

        # 3. Walk students, skipping applicants
        students = StudentProfile.objects.select_related('current_level', 'current_session')
        promoted = Counter()
        final_level = Counter()
        skipped_applicants = 0

        with transaction.atomic():
            for student in students:
                level = student.current_level

                if level is None or level.name.startswith('APP_'):
                    skipped_applicants += 1
                    continue

                nxt = next_level_for.get(level.pk)

                if nxt is None:
                    # Already at the top of their programme - session still moves,
                    # level is left alone. These need a graduation decision.
                    final_level[f"{level.programme_type} {level.name}"] += 1
                    student.current_session = target_session
                else:
                    promoted[f"{level.programme_type} {level.name} -> {nxt.name}"] += 1
                    student.current_level = nxt
                    student.current_semester = 'first'
                    student.current_session = target_session

                if not dry_run:
                    student.save(update_fields=[
                        'current_level', 'current_semester', 'current_session'
                    ])

            if dry_run:
                transaction.set_rollback(True)

        # 4. Summary
        self.stdout.write("\nSummary:")
        for key, n in sorted(promoted.items()):
            self.stdout.write(f"  {key:<32} {n}")
        for key, n in sorted(final_level.items()):
            self.stdout.write(self.style.WARNING(
                f"  {key} already at final level - session moved, level unchanged: {n}"
            ))
        if skipped_applicants:
            self.stdout.write(f"  Applicants skipped: {skipped_applicants}")
        self.stdout.write(f"  Total promoted: {sum(promoted.values())}")
        self.stdout.write(f"  Total students: {students.count()}")

        if dry_run:
            self.stdout.write(self.style.WARNING(
                "\nDry run - nothing was written. Re-run without --dry-run to apply."
            ))
        else:
            self.stdout.write(self.style.SUCCESS("\nDone."))
