# Generated by Django 4.2 on 2024-04-24 19:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admins', '0017_alter_order_options_rename_user_order_client_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shipping_charges',
            field=models.FloatField(default=0),
        ),
    ]