# Generated by Django 3.1.5 on 2021-01-24 00:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='is_done',
            field=models.BooleanField(default=False),
        ),
    ]
