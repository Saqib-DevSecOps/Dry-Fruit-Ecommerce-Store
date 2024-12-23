# Generated by Django 4.2.11 on 2024-05-26 20:42

from django.db import migrations, models
import src.administration.admins.models


class Migration(migrations.Migration):

    dependencies = [
        ('admins', '0043_order_service_type_order_tax'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='tax',
        ),
        migrations.AddField(
            model_name='product',
            name='cgst',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True, validators=[src.administration.admins.models.positive_validator]),
        ),
        migrations.AddField(
            model_name='product',
            name='igst',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True, validators=[src.administration.admins.models.positive_validator]),
        ),
        migrations.AddField(
            model_name='product',
            name='sgst',
            field=models.DecimalField(decimal_places=2, max_digits=10, null=True, validators=[src.administration.admins.models.positive_validator]),
        ),
    ]
