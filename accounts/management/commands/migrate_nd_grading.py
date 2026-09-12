from django.core.management.base import BaseCommand
from accounts.models import Result, StudentProfile, SemesterGPA

class Command(BaseCommand):
    help = 'Migrates existing ND results to the new 4.0 grading scale and recalculates GPAs'

    def handle(self, *args, **options):
        # 1. Update all ND Results to the 4.0 scale
        self.stdout.write(self.style.SUCCESS("Starting ND Result migration..."))
        nd_results = Result.objects.filter(student__programme_type='nd')
        count = 0
        for result in nd_results:
            # This triggers the updated save() logic in the model
            result.save()
            count += 1
        self.stdout.write(self.style.SUCCESS(f"Successfully updated {count} ND results."))

        # 2. Recalculate GPAs for all ND students to reflect the new points
        self.stdout.write(self.style.SUCCESS("Recalculating GPAs for ND students..."))
        nd_students = StudentProfile.objects.filter(programme_type='nd')
        for student in nd_students:
            gpas = SemesterGPA.objects.filter(student=student)
            for gpa_record in gpas:
                gpa_record.calculate_gpa()
                gpa_record.calculate_cgpa()
                gpa_record.save()
            
            # Update the student's main CGPA field
            if gpas.exists():
                latest_gpa = gpas.latest('academic_session__start_date', 'semester')
                student.cgpa = latest_gpa.cgpa
                student.save()

        self.stdout.write(self.style.SUCCESS("Migration Complete! All ND students are now on the 4.0 scale and their GPAs have been updated."))
