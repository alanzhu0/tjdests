# Generated by Django 3.2 on 2021-04-22 17:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("destinations", "0008_alter_decision_admission_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="decision",
            name="admission_status",
            field=models.CharField(
                choices=[
                    ("ADMIT", "Admitted"),
                    ("WAITLIST", "Waitlisted"),
                    ("WAITLIST_ADMIT", "Waitlist-Admitted"),
                    ("WAITLIST_DENY", "Waitlist-Denied"),
                    ("DEFER", "Deferred"),
                    ("DEFER_ADMIT", "Deferred-Admitted"),
                    ("DEFER_DENY", "Deferred-Denied"),
                    ("DEFER_WAITLIST", "Deferred-Waitlisted"),
                    ("DEFER_WAITLIST_ADMIT", "Deferred-Waitlisted-Admitted"),
                    ("DEFER_WAITLIST_DENY", "Deferred-Waitlisted-Denied"),
                    ("DENY", "Denied"),
                ],
                max_length=20,
            ),
        ),
    ]
