# Generated by Django 3.1.5 on 2021-01-23 22:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseMaterial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
            ],
            options={
                'db_table': 'base_materials',
            },
        ),
        migrations.CreateModel(
            name='DrinkCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
            ],
            options={
                'db_table': 'drink_categories',
            },
        ),
        migrations.CreateModel(
            name='DrinkDetail',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('alcohol_content', models.DecimalField(decimal_places=1, max_digits=3)),
                ('fragrance', models.CharField(max_length=100, null=True)),
                ('flavor', models.CharField(max_length=100, null=True)),
                ('finish', models.CharField(max_length=100, null=True)),
                ('with_who', models.CharField(max_length=2000, null=True)),
                ('what_situation', models.CharField(max_length=2000, null=True)),
                ('what_mood', models.CharField(max_length=2000, null=True)),
                ('what_profit', models.CharField(max_length=2000, null=True)),
                ('recommend_situation', models.CharField(max_length=2000, null=True)),
                ('recommend_eating_method', models.CharField(max_length=2000, null=True)),
                ('additional_info', models.CharField(max_length=2000, null=True)),
                ('drink_category', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.drinkcategory')),
            ],
            options={
                'db_table': 'drink_details',
            },
        ),
        migrations.CreateModel(
            name='Manufacture',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
                ('origin', models.CharField(max_length=45)),
                ('representative_name', models.CharField(max_length=20)),
                ('email', models.EmailField(max_length=100)),
                ('phone_number', models.CharField(max_length=11)),
                ('address', models.CharField(max_length=200)),
                ('company_registration_number', models.CharField(max_length=10)),
                ('mail_order_report_number', models.CharField(max_length=20)),
            ],
            options={
                'db_table': 'manufactures',
            },
        ),
        migrations.CreateModel(
            name='ManufactureType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
            ],
            options={
                'db_table': 'manufacture_types',
            },
        ),
        migrations.CreateModel(
            name='Paring',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
                ('description', models.TextField(null=True)),
            ],
            options={
                'db_table': 'parings',
            },
        ),
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
                ('subtitle', models.CharField(max_length=100, null=True)),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('content', models.TextField(null=True)),
                ('is_damhwa_box', models.BooleanField(default=False)),
                ('discount_rate', models.FloatField(null=True)),
                ('selling_count', models.IntegerField(default=0)),
                ('hit_count', models.IntegerField(default=0)),
                ('award', models.CharField(max_length=100, null=True)),
                ('star_rating', models.DecimalField(decimal_places=1, default=0, max_digits=2)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('manufacture', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.manufacture')),
            ],
            options={
                'db_table': 'products',
            },
        ),
        migrations.CreateModel(
            name='ProductCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
            ],
            options={
                'db_table': 'Product_categories',
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
            ],
            options={
                'db_table': 'tags',
            },
        ),
        migrations.CreateModel(
            name='Volume',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=45)),
            ],
            options={
                'db_table': 'volumes',
            },
        ),
        migrations.CreateModel(
            name='TasteMatrix',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('body', models.DecimalField(decimal_places=1, max_digits=2)),
                ('acidity', models.DecimalField(decimal_places=1, max_digits=2)),
                ('sweetness', models.DecimalField(decimal_places=1, max_digits=2)),
                ('tannin', models.DecimalField(decimal_places=1, max_digits=2)),
                ('bitter', models.DecimalField(decimal_places=1, max_digits=2)),
                ('sparkling', models.DecimalField(decimal_places=1, max_digits=2)),
                ('light', models.DecimalField(decimal_places=1, max_digits=2)),
                ('turbidity', models.DecimalField(decimal_places=1, max_digits=2)),
                ('savory', models.DecimalField(decimal_places=1, max_digits=2)),
                ('gorgeous', models.DecimalField(decimal_places=1, max_digits=2)),
                ('spicy', models.DecimalField(decimal_places=1, max_digits=2)),
                ('drink_detail', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.drinkdetail')),
            ],
            options={
                'db_table': 'taste_matrixs',
            },
        ),
        migrations.CreateModel(
            name='ProductTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.product')),
                ('tag', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.tag')),
            ],
            options={
                'db_table': 'product_tags',
            },
        ),
        migrations.CreateModel(
            name='ProductImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image_url', models.URLField(max_length=2000)),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.product')),
            ],
            options={
                'db_table': 'product_images',
            },
        ),
        migrations.AddField(
            model_name='product',
            name='product_category',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.productcategory'),
        ),
        migrations.AddField(
            model_name='product',
            name='product_tag',
            field=models.ManyToManyField(related_name='product_tag_set', through='product.ProductTag', to='product.Tag'),
        ),
        migrations.AddField(
            model_name='product',
            name='uploader',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='user.administrator'),
        ),
        migrations.AddField(
            model_name='manufacture',
            name='manufacture_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.manufacturetype'),
        ),
        migrations.CreateModel(
            name='Label',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label_url', models.URLField(max_length=2000)),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.product')),
            ],
            options={
                'db_table': 'labels',
            },
        ),
        migrations.CreateModel(
            name='IndustrialProductInfo',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('food_type', models.CharField(max_length=45)),
                ('business_name', models.CharField(max_length=45)),
                ('location', models.CharField(max_length=200)),
                ('shelf_life', models.CharField(max_length=100)),
                ('volume_by_packing', models.IntegerField(default=1)),
                ('base_material_name_and_content', models.CharField(max_length=200)),
                ('nutrient', models.CharField(max_length=200)),
                ('gmo', models.CharField(max_length=45)),
                ('Import_declaration', models.CharField(max_length=200)),
                ('product', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.product')),
            ],
            options={
                'db_table': 'industrial_product_infos',
            },
        ),
        migrations.CreateModel(
            name='DrinkDetailVolume',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('price', models.DecimalField(decimal_places=2, max_digits=10)),
                ('drink_detail', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.drinkdetail')),
                ('volume', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.volume')),
            ],
            options={
                'db_table': 'drink_detail_volumes',
            },
        ),
        migrations.CreateModel(
            name='DrinkDetailParing',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('drink_detail', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.drinkdetail')),
                ('paring', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.paring')),
            ],
            options={
                'db_table': 'drink_detail_parings',
            },
        ),
        migrations.CreateModel(
            name='DrinkDetailBaseMaterial',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('base_material', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.basematerial')),
                ('drink_detail', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.drinkdetail')),
            ],
            options={
                'db_table': 'drink_detail_base_materials',
            },
        ),
        migrations.AddField(
            model_name='drinkdetail',
            name='drink_detail_base_material',
            field=models.ManyToManyField(related_name='drink_detail_base_material_set', through='product.DrinkDetailBaseMaterial', to='product.BaseMaterial'),
        ),
        migrations.AddField(
            model_name='drinkdetail',
            name='drink_detail_paring',
            field=models.ManyToManyField(related_name='drink_detail_paring_set', through='product.DrinkDetailParing', to='product.Paring'),
        ),
        migrations.AddField(
            model_name='drinkdetail',
            name='drink_detail_volume',
            field=models.ManyToManyField(related_name='drink_detail_volume_set', through='product.DrinkDetailVolume', to='product.Volume'),
        ),
        migrations.AddField(
            model_name='drinkdetail',
            name='product',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='product.product'),
        ),
    ]
