# Generated by Django 5.2.3 on 2025-06-28 07:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='complaints',
            name='status',
            field=models.CharField(choices=[('Pending', 'Pending'), ('In Progress', 'In Progress'), ('Closed', 'Closed'), ('Escalated', 'Escalated')], default='Pending'),
        ),
    ]
