# Generated by Django 5.2.3 on 2025-07-07 09:59

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("products", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="category",
            name="image",
            field=cloudinary.models.CloudinaryField(
                blank=True, max_length=255, null=True, verbose_name="category_image"
            ),
        ),
    ]
