# Generated by Django 5.1 on 2024-08-12 09:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("renthub", "0002_property_city"),
    ]

    operations = [
        migrations.AddField(
            model_name="property",
            name="property_type",
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
