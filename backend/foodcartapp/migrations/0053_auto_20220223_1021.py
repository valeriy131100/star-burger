# Generated by Django 3.2 on 2022-02-23 07:21

from django.db import migrations


def fix_typo_in_order_pay_by_default_value(apps, schema_editor):
    Order = apps.get_model(
        'foodcartapp',
        'Order'
    )

    Order.objects.filter(pay_by='not chose').update(pay_by='not chosen')


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0052_alter_order_restaurant'),
    ]

    operations = [
        migrations.RunPython(fix_typo_in_order_pay_by_default_value)
    ]
