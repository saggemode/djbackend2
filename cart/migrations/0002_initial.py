# Generated by Django 5.2.1 on 2025-06-21 17:16

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('cart', '0001_initial'),
        ('product', '0001_initial'),
        ('store', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='cart',
            name='product',
            field=models.ForeignKey(db_column='productId_id', on_delete=django.db.models.deletion.CASCADE, to='product.product'),
        ),
        migrations.AddField(
            model_name='cart',
            name='store',
            field=models.ForeignKey(db_column='storeId_id', on_delete=django.db.models.deletion.CASCADE, to='store.store'),
        ),
        migrations.AddField(
            model_name='cart',
            name='user',
            field=models.ForeignKey(db_column='userId_id', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='cart',
            name='variant',
            field=models.ForeignKey(blank=True, db_column='variantId_id', null=True, on_delete=django.db.models.deletion.CASCADE, to='product.productvariant'),
        ),
        migrations.AlterUniqueTogether(
            name='cart',
            unique_together={('user', 'store', 'product', 'variant')},
        ),
    ]
