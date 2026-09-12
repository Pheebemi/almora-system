# Generated data migration: set existing faculties to degree, add ND/NCE levels

from django.db import migrations


def set_faculty_programme_type(apps, schema_editor):
    Faculty = apps.get_model('accounts', 'Faculty')
    Faculty.objects.filter(programme_type__isnull=True).update(programme_type='degree')
    # Also set any empty string to degree
    Faculty.objects.filter(programme_type='').update(programme_type='degree')


def add_nd_nce_levels(apps, schema_editor):
    Level = apps.get_model('accounts', 'Level')
    # Use orders that don't conflict with existing (100, 200, 300, 400 typically use 1,2,3,4; screening may use 999+)
    existing_orders = set(Level.objects.values_list('order', flat=True))
    next_order = max(existing_orders) + 1 if existing_orders else 5
    to_create = []
    # ND1, ND2
    for name, display_name in [('ND1', 'ND 1'), ('ND2', 'ND 2')]:
        if not Level.objects.filter(name=name).exists():
            to_create.append(Level(
                name=name,
                display_name=display_name,
                order=next_order,
                programme_type='nd',
                is_active=True
            ))
            next_order += 1
    # NCE1, NCE2
    for name, display_name in [('NCE1', 'NCE 1'), ('NCE2', 'NCE 2')]:
        if not Level.objects.filter(name=name).exists():
            to_create.append(Level(
                name=name,
                display_name=display_name,
                order=next_order,
                programme_type='nce',
                is_active=True
            ))
            next_order += 1
    if to_create:
        Level.objects.bulk_create(to_create)


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0027_add_programme_type'),
    ]

    operations = [
        migrations.RunPython(set_faculty_programme_type, noop),
        migrations.RunPython(add_nd_nce_levels, noop),
    ]
