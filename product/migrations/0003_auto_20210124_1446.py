# Generated by Django 3.1.5 on 2021-01-24 14:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0002_product_is_done'),
    ]

    operations = [
        migrations.RenameField(
            model_name='industrialproductinfo',
            old_name='Import_declaration',
            new_name='import_declaration',
        ),
    ]
