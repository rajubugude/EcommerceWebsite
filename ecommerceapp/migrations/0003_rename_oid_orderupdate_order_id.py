# Generated by Django 4.2.1 on 2023-05-28 12:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('ecommerceapp', '0002_rename_order_id_orderupdate_oid'),
    ]

    operations = [
        migrations.RenameField(
            model_name='orderupdate',
            old_name='oid',
            new_name='order_id',
        ),
    ]