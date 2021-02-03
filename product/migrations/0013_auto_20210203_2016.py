# Generated by Django 3.1.5 on 2021-02-03 20:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0012_auto_20210203_1453'),
    ]

    operations = [
        migrations.AlterField(
            model_name='industrialproductinfo',
            name='base_material_name_and_content',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='industrialproductinfo',
            name='business_name',
            field=models.CharField(max_length=45, null=True),
        ),
        migrations.AlterField(
            model_name='industrialproductinfo',
            name='food_type',
            field=models.CharField(max_length=45, null=True),
        ),
        migrations.AlterField(
            model_name='industrialproductinfo',
            name='gmo',
            field=models.CharField(max_length=45, null=True),
        ),
        migrations.AlterField(
            model_name='industrialproductinfo',
            name='import_declaration',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='industrialproductinfo',
            name='location',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='industrialproductinfo',
            name='nutrient',
            field=models.CharField(max_length=200, null=True),
        ),
        migrations.AlterField(
            model_name='industrialproductinfo',
            name='shelf_life',
            field=models.CharField(max_length=100, null=True),
        ),
        migrations.AlterField(
            model_name='industrialproductinfo',
            name='volume_by_packing',
            field=models.CharField(max_length=45, null=True),
        ),
    ]
