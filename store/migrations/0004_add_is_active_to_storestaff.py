# Generated by Django 5.2.1 on 2025-06-28 21:10:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0003_alter_store_auto_approve_products_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='storestaff',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]

    def database_forwards(self, app_label, schema_editor, from_state, to_state):
        # Check if column already exists
        with schema_editor.connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'store_storestaff' 
                AND column_name = 'is_active'
            """)
            if cursor.fetchone():
                # Column already exists, skip the operation
                return
        
        # Column doesn't exist, proceed with normal operation
        super().database_forwards(app_label, schema_editor, from_state, to_state) 