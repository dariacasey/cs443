# Generated by Django 4.2.4 on 2023-12-03 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbInterface', '0006_order_quantity'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='card',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
