from accounts.models import Department, Level, AcademicSession

def check_data():
    depts = Department.objects.filter(name__icontains='Accounting')
    print("Departments found:")
    for d in depts:
        print(f"ID: {d.id}, Name: {d.name}, Short Name: {d.short_name}")
    
    levels = Level.objects.filter(name__icontains='200')
    print("\nLevels found:")
    for l in levels:
        print(f"ID: {l.id}, Name: {l.name}, Display Name: {l.display_name}")
        
    session = AcademicSession.objects.filter(is_active=True).first()
    print(f"\nActive Session: {session.name if session else 'None'}")

if __name__ == "__main__":
    check_data()
