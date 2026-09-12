from django.core.management.base import BaseCommand
from accounts.models import AcademicSession, Department, Level, FeeStructure, Faculty


class Command(BaseCommand):
    help = 'Populate initial fee structures for departments, levels (Degree/ND/NCE), and applicant/screening fees'

    def handle(self, *args, **options):
        # Get active academic session
        try:
            current_session = AcademicSession.objects.filter(is_active=True).first()
            if not current_session:
                current_session = AcademicSession.objects.filter(name="2023/2024").first()
            if not current_session:
                self.stdout.write(self.style.ERROR('No academic session found. Please create one first.'))
                return
        except AcademicSession.DoesNotExist:
            self.stdout.write(self.style.ERROR('No academic session found. Please create one first.'))
            return

        # Default fee amounts by level name (Degree 100–400, ND, NCE)
        default_fees = {
            '100': 150000,
            '200': 120000,
            '300': 120000,
            '400': 120000,
            'ND1': 100000,
            'ND2': 100000,
            'NCE1': 80000,
            'NCE2': 80000,
        }

        # --- Department + Level fee structures (only for matching programme type) ---
        departments = Department.objects.select_related('faculty').all()
        levels = Level.objects.filter(is_active=True)

        if not departments:
            self.stdout.write(self.style.ERROR('No departments found. Please create departments first.'))
            return

        if not levels:
            self.stdout.write(self.style.ERROR('No levels found. Please create levels first.'))
            return

        created_count = 0
        updated_count = 0

        for department in departments:
            dept_programme = getattr(department.faculty, 'programme_type', 'degree') or 'degree'
            for level in levels:
                if level.programme_type != dept_programme:
                    continue
                level_name = level.name
                if level_name not in default_fees:
                    continue
                fee_amount = default_fees[level_name]

                fee_structure, created = FeeStructure.objects.get_or_create(
                    academic_session=current_session,
                    department=department,
                    level=level,
                    defaults={'amount': fee_amount}
                )

                if created:
                    self.stdout.write(f'Created: {current_session.name} / {department.name} / {level.display_name} - NGN {fee_amount}')
                    created_count += 1
                else:
                    if fee_structure.amount != fee_amount:
                        old_amount = fee_structure.amount
                        fee_structure.amount = fee_amount
                        fee_structure.save()
                        self.stdout.write(f'Updated: {current_session.name} / {department.name} / {level.display_name} - NGN {old_amount} -> NGN {fee_amount}')
                        updated_count += 1

        # --- Applicant / Screening fee structures ---
        admin_faculty, _ = Faculty.objects.get_or_create(
            short_name='ADMIN',
            programme_type='degree',
            defaults={'name': 'Central Administration'}
        )
        screening_dept, _ = Department.objects.get_or_create(
            faculty=admin_faculty,
            short_name='SCREENING',
            defaults={'name': 'Screening'}
        )
        applicant_level_names = [
            ('APP_DEG', 'Applicant (Degree)', 'degree', 90),
            ('APP_ND', 'Applicant (ND)', 'nd', 91),
            ('APP_NCE', 'Applicant (NCE)', 'nce', 92),
        ]
        applicant_fees = {
            'APP_DEG': 12000,
            'APP_ND': 5000,
            'APP_NCE': 5000,
        }
        for name, display_name, prog_type, order in applicant_level_names:
            level, _ = Level.objects.get_or_create(
                name=name,
                defaults={
                    'display_name': display_name,
                    'programme_type': prog_type,
                    'order': order,
                    'is_active': True,
                }
            )
            amount = applicant_fees[name]
            fs, created = FeeStructure.objects.get_or_create(
                academic_session=current_session,
                department=screening_dept,
                level=level,
                defaults={'amount': amount}
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Applicant fee: {current_session.name} / {screening_dept.name} / {level.display_name} - NGN {amount}'))
                created_count += 1
            elif fs.amount != amount:
                fs.amount = amount
                fs.save()
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Fee structure population completed. Created: {created_count}, Updated: {updated_count}'
            )
        )