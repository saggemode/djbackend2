# Generated by Django 5.2.1 on 2025-06-28 21:11

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0004_add_is_active_to_storestaff'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveIndex(
            model_name='storestaff',
            name='store_store_store_i_abbfa2_idx',
        ),
        migrations.RemoveIndex(
            model_name='storestaff',
            name='store_store_user_id_76d4f5_idx',
        ),
        migrations.RemoveIndex(
            model_name='storestaff',
            name='store_store_role_91af2a_idx',
        ),
        migrations.AlterField(
            model_name='storestaff',
            name='is_active',
            field=models.BooleanField(default=True, help_text='Whether the staff member is active'),
        ),
        migrations.AddIndex(
            model_name='storestaff',
            index=models.Index(fields=['store', 'role'], name='store_store_store_i_cbb8e7_idx'),
        ),
        migrations.AddIndex(
            model_name='storestaff',
            index=models.Index(fields=['user', 'role'], name='store_store_user_id_99c72e_idx'),
        ),
        migrations.AddIndex(
            model_name='storestaff',
            index=models.Index(fields=['role', 'deleted_at'], name='store_store_role_59dbdf_idx'),
        ),
    ]
