# Generated by Django 5.1.7 on 2025-03-27 19:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('documents', '0002_documentrevision_design_ownership_and_more'),
        ('organization', '0002_location_alter_role_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='documentrevision',
            old_name='purpose_and_scope',
            new_name='process_purpose_and_scope',
        ),
        migrations.RenameField(
            model_name='documentrevisionoutputpart',
            old_name='outout_part',
            new_name='output_part',
        ),
        migrations.RemoveField(
            model_name='documentrevision',
            name='set_role_by_step',
        ),
        migrations.AddField(
            model_name='documentrevision',
            name='device_identifier_number',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='documentrevision',
            name='process_locations',
            field=models.ManyToManyField(blank=True, to='organization.location'),
        ),
        migrations.AddField(
            model_name='documentrevision',
            name='process_roles',
            field=models.ManyToManyField(blank=True, to='organization.role'),
        ),
        migrations.AddField(
            model_name='documentrevision',
            name='process_set_locations_by_step',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='documentrevision',
            name='process_set_roles_by_step',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='documentrevisionprocessstep',
            name='locations',
            field=models.ManyToManyField(blank=True, to='organization.location'),
        ),
        migrations.AlterUniqueTogether(
            name='documentrevisioninputpart',
            unique_together={('document_revision', 'input_part')},
        ),
        migrations.AlterUniqueTogether(
            name='documentrevisionoutputpart',
            unique_together={('document_revision', 'output_part')},
        ),
    ]
