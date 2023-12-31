# Generated by Django 4.2.7 on 2023-11-29 05:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("dbInterface", "0003_product_quantity"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="cart",
            name="productID",
        ),
        migrations.RemoveField(
            model_name="product",
            name="quantity",
        ),
        migrations.AddField(
            model_name="cart",
            name="products",
            field=models.ManyToManyField(to="dbInterface.product"),
        ),
    ]
