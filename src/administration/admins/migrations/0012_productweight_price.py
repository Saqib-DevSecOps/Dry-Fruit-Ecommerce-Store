# Generated by Django 4.2 on 2024-04-20 10:26

from django.db import migrations, models
import src.administration.admins.models


class Migration(migrations.Migration):

    dependencies = [
        ('admins', '0011_weight_remove_product_weight_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='productweight',
            name='price',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, validators=[src.administration.admins.models.positive_validator]),
        ),
    ]
