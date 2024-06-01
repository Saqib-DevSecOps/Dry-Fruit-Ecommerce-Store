# Generated by Django 4.2 on 2024-04-02 20:11

from django.db import migrations, models
import src.administration.admins.models


class Migration(migrations.Migration):

    dependencies = [
        ('admins', '0005_productweight_remove_product_height_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='height',
            field=models.FloatField(blank=True, help_text='measurement in inches', null=True, validators=[src.administration.admins.models.positive_validator]),
        ),
        migrations.AddField(
            model_name='product',
            name='length',
            field=models.FloatField(blank=True, help_text='measurement in inches', null=True, validators=[src.administration.admins.models.positive_validator]),
        ),
        migrations.AddField(
            model_name='product',
            name='width',
            field=models.FloatField(blank=True, help_text='measurement in inches', null=True, validators=[src.administration.admins.models.positive_validator]),
        ),
        migrations.AlterField(
            model_name='product',
            name='weight',
            field=models.FloatField(blank=True, help_text='weight in grams', null=True, validators=[src.administration.admins.models.positive_validator]),
        ),
    ]