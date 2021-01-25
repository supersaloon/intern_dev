# Generated by Django 3.1.5 on 2021-01-25 01:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0003_auto_20210124_1446'),
    ]

    operations = [
        migrations.AlterField(
            model_name='drinkdetailbasematerial',
            name='drink_detail',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='product.drinkdetail'),
        ),
        migrations.AlterField(
            model_name='drinkdetailparing',
            name='drink_detail',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='product.drinkdetail'),
        ),
        migrations.AlterField(
            model_name='drinkdetailvolume',
            name='drink_detail',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='product.drinkdetail'),
        ),
        migrations.AlterField(
            model_name='producttag',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='product.product'),
        ),
    ]