# Generated by Django 5.2.1 on 2025-06-27 14:19

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
            name='updated_by',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='updated_cart_items', to=settings.AUTH_USER_MODEL),
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
        migrations.AddIndex(
            model_name='cart',
            index=models.Index(fields=['user', 'is_deleted'], name='cart_cart_userId__7968f3_idx'),
        ),
        migrations.AddIndex(
            model_name='cart',
            index=models.Index(fields=['store', 'is_deleted'], name='cart_cart_storeId_823d5a_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='cart',
            unique_together={('user', 'store', 'product', 'variant')},
        ),
    ]
