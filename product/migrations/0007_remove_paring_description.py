# Generated by Django 3.1.5 on 2021-01-30 11:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0006_auto_20210128_1326'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='paring',
            name='description',
        ),
    ]