# Generated by Django 2.2.1 on 2019-07-16 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('projects', '0019_auto_20190325_1435'),
        ('assignments', '0005_auto_20190716_1136'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='assignment',
            name='students_projects',
        ),
        migrations.AddField(
            model_name='assignment',
            name='student_projects',
            field=models.ManyToManyField(related_name='student_assignments', through='assignments.StudentProjectThrough', to='projects.Project'),
        ),
    ]
