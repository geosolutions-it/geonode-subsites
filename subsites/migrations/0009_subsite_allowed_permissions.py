# Generated by Django 3.2.22 on 2023-10-23 13:10

import django.contrib.postgres.fields
from django.db import migrations, models


def set_min_perms(apps, schema_editor):
    # We get the model from the versioned app registry;
    # if we directly import it, it'll be the wrong version
    subsites = apps.get_model("subsites", "SubSite")
    subsites.objects.update(allowed_permissions=["view", "download"])


class Migration(migrations.Migration):
    dependencies = [
        ("subsites", "0008_auto_20231006_0827"),
    ]

    operations = [
        migrations.AddField(
            model_name="subsite",
            name="allowed_permissions",
            field=django.contrib.postgres.fields.ArrayField(
                base_field=models.CharField(max_length=100),
                blank=True,
                default=list,
                help_text="Max allowed permission that the user can have in the subsite. No additional permissions are assinged to the user",
                max_length=100,
                null=True,
                size=None,
            ),
        ),
        migrations.RunPython(set_min_perms, migrations.RunPython.noop)
    ]
