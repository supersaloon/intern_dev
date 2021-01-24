from django.db import models


class ProductCategory(models.Model):
    name = models.CharField(max_length=45)

    class Meta:
        db_table = 'Product_categories'


# 태그
class Tag(models.Model):
    name = models.CharField(max_length=45)

    class Meta:
        db_table = 'tags'


# product to tag 중간 테이블
class ProductTag(models.Model):
    product = models.ForeignKey('Product', on_delete=models.SET_NULL, null=True)
    tag     = models.ForeignKey(Tag, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'product_tags'


# 제조자 타입: 양조장, 공산품 등등
class ManufactureType(models.Model):
    name = models.CharField(max_length=45)

    class Meta:
        db_table = 'manufacture_types'


# 공산품 제조자 정보
class Manufacture(models.Model):
    manufacture_type            = models.ForeignKey(ManufactureType, on_delete=models.SET_NULL, null=True)
    name                        = models.CharField(max_length=45)
    origin                      = models.CharField(max_length=45)
    representative_name         = models.CharField(max_length=20)
    email                       = models.EmailField(max_length=100)
    phone_number                = models.CharField(max_length=11)
    address                     = models.CharField(max_length=200)
    company_registration_number = models.CharField(max_length=10)
    mail_order_report_number    = models.CharField(max_length=20)

    class Meta:
        db_table = 'manufactures'


class Product(models.Model):
    # 중간 테이블 사용하는 필드
    product_tag      = models.ManyToManyField(Tag, through='ProductTag', related_name='product_tag_set')

    name             = models.CharField(max_length=45)
    subtitle         = models.CharField(max_length=100, null=True)
    price            = models.DecimalField(max_digits=10, decimal_places=2)
    content          = models.TextField(null=True)
    is_damhwa_box    = models.BooleanField(default=False)
    discount_rate    = models.FloatField(null=True)
    selling_count    = models.IntegerField(default=0)
    hit_count        = models.IntegerField(default=0)
    award            = models.CharField(max_length=100, null=True)
    star_rating      = models.DecimalField(max_digits=2, decimal_places=1, default=0)
    product_category = models.ForeignKey(ProductCategory, on_delete = models.SET_NULL, null=True)
    manufacture      = models.ForeignKey(Manufacture, on_delete=models.SET_NULL, null=True)
    uploader         = models.ForeignKey('user.Administrator', on_delete=models.SET_NULL, null=True)
    is_done          = models.BooleanField(default=False)
    created_at       = models.DateTimeField(auto_now_add = True)
    updated_at       = models.DateTimeField(auto_now = True)

    class Meta:
        db_table = 'products'


class ProductImage(models.Model):
    product   = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    image_url = models.URLField(max_length=2000)

    class Meta:
        db_table = 'product_images'


class IndustrialProductInfo(models.Model):
    product                        = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    food_type                      = models.CharField(max_length=45)
    business_name                  = models.CharField(max_length=45)
    location                       = models.CharField(max_length=200)
    shelf_life                     = models.CharField(max_length=100)
    volume_by_packing              = models.IntegerField(default=1)
    base_material_name_and_content = models.CharField(max_length=200)
    nutrient                       = models.CharField(max_length=200)
    gmo                            = models.CharField(max_length=45)
    import_declaration             = models.CharField(max_length=200)

    class Meta:
        db_table = 'industrial_product_infos'


class Label(models.Model):
    product   = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    label_url = models.URLField(max_length=2000)

    class Meta:
        db_table = 'labels'


# 페어링
class Paring(models.Model):
    name        = models.CharField(max_length=45)
    description = models.TextField(null=True)

    class Meta:
        db_table = 'parings'


# drink_detail to paring 중간 테이블
class DrinkDetailParing(models.Model):
    drink_detail = models.ForeignKey('DrinkDetail', on_delete=models.SET_NULL, null=True)
    paring       = models.ForeignKey(Paring, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'drink_detail_parings'


# 원재료
class BaseMaterial(models.Model):
    name = models.CharField(max_length=45)

    class Meta:
        db_table = 'base_materials'


# drink_detail to base_material 중간 테이블
class DrinkDetailBaseMaterial(models.Model):
    drink_detail  = models.ForeignKey('DrinkDetail', on_delete=models.SET_NULL, null=True)
    base_material = models.ForeignKey(BaseMaterial, on_delete=models.SET_NULL, null=True)

    class Meta:
        db_table = 'drink_detail_base_materials'


# 용량
class Volume(models.Model):
    name = models.CharField(max_length=45)

    class Meta:
        db_table = 'volumes'


# 주류 용량(및 가격) 중간 테이블
class DrinkDetailVolume(models.Model):
    drink_detail = models.ForeignKey('DrinkDetail', on_delete=models.SET_NULL, null=True)
    volume       = models.ForeignKey(Volume, on_delete=models.SET_NULL, null=True)
    price        = models.DecimalField(max_digits = 10, decimal_places = 2)

    class Meta:
        db_table = 'drink_detail_volumes'


class DrinkCategory(models.Model):
    name = models.CharField(max_length=45)

    class Meta:
        db_table = 'drink_categories'


class DrinkDetail(models.Model):
    product                    = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    drink_category             = models.ForeignKey(DrinkCategory, on_delete=models.SET_NULL, null=True)

    drink_detail_volume        = models.ManyToManyField(Volume, through=DrinkDetailVolume, related_name='drink_detail_volume_set')
    drink_detail_base_material = models.ManyToManyField(BaseMaterial, through=DrinkDetailBaseMaterial, related_name='drink_detail_base_material_set')
    drink_detail_paring        = models.ManyToManyField(Paring, through=DrinkDetailParing, related_name='drink_detail_paring_set')

    alcohol_content            = models.DecimalField(max_digits = 3, decimal_places = 1)
    fragrance                  = models.CharField(max_length=100, null=True)
    flavor                     = models.CharField(max_length=100, null=True)
    finish                     = models.CharField(max_length=100, null=True)
    with_who                   = models.CharField(max_length=2000, null=True)
    what_situation             = models.CharField(max_length=2000, null=True)
    what_mood                  = models.CharField(max_length=2000, null=True)
    what_profit                = models.CharField(max_length=2000, null=True)
    recommend_situation        = models.CharField(max_length=2000, null=True)
    recommend_eating_method    = models.CharField(max_length=2000, null=True)
    additional_info            = models.CharField(max_length=2000, null=True)

    class Meta:
        db_table = 'drink_details'


class TasteMatrix(models.Model):
    drink_detail = models.ForeignKey(DrinkDetail, on_delete=models.SET_NULL, null=True)
    body         = models.DecimalField(max_digits = 2, decimal_places = 1)
    acidity      = models.DecimalField(max_digits = 2, decimal_places = 1)
    sweetness    = models.DecimalField(max_digits = 2, decimal_places = 1)
    tannin       = models.DecimalField(max_digits = 2, decimal_places = 1)
    bitter       = models.DecimalField(max_digits = 2, decimal_places = 1)
    sparkling    = models.DecimalField(max_digits = 2, decimal_places = 1)
    light        = models.DecimalField(max_digits = 2, decimal_places = 1)
    turbidity    = models.DecimalField(max_digits = 2, decimal_places = 1)
    savory       = models.DecimalField(max_digits = 2, decimal_places = 1)
    gorgeous     = models.DecimalField(max_digits = 2, decimal_places = 1)
    spicy        = models.DecimalField(max_digits = 2, decimal_places = 1)

    class Meta:
        db_table = 'taste_matrixs'

