# Generated by Django 3.1.5 on 2021-02-02 15:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0009_drinkdetailvolume_amount'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='DrinkDetailVolume',
            new_name='DrinkOption',
        ),
        migrations.AlterModelTable(
            name='drinkoption',
            table='drink_options',
        ),
    ]
