# Simple migration to create models without data conversion

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0020_remove_academicrecord_courses_academicrecord_courses'),
    ]

    operations = [
        migrations.CreateModel(
            name='AcademicSession',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="e.g., '2023/2024'", max_length=20, unique=True)),
                ('start_year', models.PositiveIntegerField(help_text='Starting year, e.g., 2023')),
                ('end_year', models.PositiveIntegerField(help_text='Ending year, e.g., 2024')),
                ('session_type', models.CharField(choices=[('regular', 'Regular Session'), ('special', 'Special Session')], default='regular', max_length=10)),
                ('is_active', models.BooleanField(default=False, help_text='Only one session can be active at a time')),
                ('start_date', models.DateField(help_text='Session start date')),
                ('end_date', models.DateField(help_text='Session end date')),
                ('registration_deadline', models.DateField(help_text='Last date for course registration')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Academic Session',
                'verbose_name_plural': 'Academic Sessions',
                'ordering': ['-start_year', '-end_year'],
            },
        ),
        migrations.CreateModel(
            name='Level',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="e.g., '100', '200'", max_length=10, unique=True)),
                ('display_name', models.CharField(help_text="e.g., '100 Level', '200 Level'", max_length=20)),
                ('order', models.PositiveIntegerField(help_text='Order for progression (1 for 100, 2 for 200, etc.)', unique=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'verbose_name': 'Academic Level',
                'verbose_name_plural': 'Academic Levels',
                'ordering': ['order'],
            },
        ),
        migrations.AddField(
            model_name='studentprofile',
            name='current_session',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='students', to='accounts.academicsession'),
        ),
    ]