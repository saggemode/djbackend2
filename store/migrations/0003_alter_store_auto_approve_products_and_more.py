# Generated by Django 5.2.1 on 2025-06-27 15:10

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0002_remove_store_store_store_status_cb0145_idx_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='store',
            name='auto_approve_products',
            field=models.BooleanField(default=True, help_text='Whether products are auto-approved for this store'),
        ),
        migrations.AlterField(
            model_name='store',
            name='commission_rate',
            field=models.DecimalField(decimal_places=2, default=0.0, help_text='Commission rate percentage (0-100)', max_digits=5, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)]),
        ),
        migrations.AlterField(
            model_name='store',
            name='is_verified',
            field=models.BooleanField(default=True, help_text='Whether the store has been verified by admin'),
        ),
        migrations.AlterField(
            model_name='store',
            name='status',
            field=models.CharField(choices=[('draft', 'Draft'), ('pending', 'Pending Review'), ('active', 'Active'), ('suspended', 'Suspended'), ('closed', 'Closed')], default='active', help_text='Current status of the store', max_length=20),
        ),
    ]
