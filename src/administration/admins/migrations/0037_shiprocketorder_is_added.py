# Generated by Django 4.2.11 on 2024-05-20 20:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admins', '0036_alter_productsize_breadth_alter_productsize_height_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='shiprocketorder',
            name='is_added',
            field=models.BooleanField(default=False),
        ),
    ]
