from django.core.management.base import BaseCommand
from core.models import ProgramChoice

class Command(BaseCommand):
    help = 'Create initial program choices for diploma, degree, and NCE programs'

    def handle(self, *args, **options):
        # Diploma choices
        diploma_choices = [
            'Computer Science',
            'Public Health',
        ]
        
        # Degree choices
        degree_choices = [
            'Adult Education',
            'Mathematics Education',
            'Economics',
            'Sociology',
            'Accounting',
        ]
        
        # NCE choices
        nce_choices = [
            'Arabic',
            'English',
            'Fulfulde',
            'Mumuye',
            'Hausa',
            'History',
        ]
        
        # Create diploma choices
        for choice in diploma_choices:
            program_choice, created = ProgramChoice.objects.get_or_create(
                program_type='diploma',
                name=choice,
                defaults={'description': f'{choice} - Diploma Program'}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created Diploma choice: {choice}')
                )
            else:
                self.stdout.write(f'Diploma choice already exists: {choice}')
        
        # Create degree choices
        for choice in degree_choices:
            program_choice, created = ProgramChoice.objects.get_or_create(
                program_type='degree',
                name=choice,
                defaults={'description': f'{choice} - Degree Program'}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created Degree choice: {choice}')
                )
            else:
                self.stdout.write(f'Degree choice already exists: {choice}')
        
        # Create NCE choices
        for choice in nce_choices:
            program_choice, created = ProgramChoice.objects.get_or_create(
                program_type='nce',
                name=choice,
                defaults={'description': f'{choice} - NCE Program'}
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created NCE choice: {choice}')
                )
            else:
                self.stdout.write(f'NCE choice already exists: {choice}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created all program choices!')
        )
