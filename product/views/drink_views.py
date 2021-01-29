import boto3
import uuid
import json

from django.http  import JsonResponse
from django.views import View
from django.db    import transaction
from django.db.utils import IntegrityError

from user.models    import Administrator
from product.models import ProductCategory, DrinkCategory, IndustrialProductInfo, Manufacture, ManufactureType, Volume, \
                           Label, TasteMatrix, DrinkDetail, DrinkDetailVolume, Product, Tag, ProductImage, Paring, BaseMaterial
from product.utils import s3_client, reverse_foreign_key_finder


class DrinkView(View):
    # @signin_decorator
    @transaction.atomic
    def post(self, request):
        try:
            data = json.loads(request.body)

            # products 테이블
            product = Product.objects.create(
                name             = data['product_name'],
                subtitle         = data['subtitle'],
                price            = data['price'],
                content          = data['content'],
                is_damhwa_box    = data['is_damhwa_box'],
                discount_rate    = data['discount_rate'],
                award            = data['award'],
                product_category = ProductCategory.objects.get(name=data['product_category']),
                manufacture      = Manufacture.objects.get(name=data['manufacture_name']),
                uploader         = Administrator.objects.get(name   = "homer"),
            )

            # product_image
            for product_image_id in data['product_image']:
                product_image = ProductImage.objects.get(id=product_image_id)
                product_image.product = product
                product_image.save()


            # label
            for label_id in data['label']:
                label = Label.objects.get(id=label_id)
                label.product = product
                label.save()


            # products 테이블에 태그 추가
            for tag in data['tag']:
                tag, flag = Tag.objects.get_or_create(name=tag)
                product.product_tag.add(tag)
                print(f"태그: {tag.name} 추가 완료")


            # industrial_product_infos 테이블
            IndustrialProductInfo.objects.create(
                product                        = product,
                food_type                      = data['food_type'],
                business_name                  = data['business_name'],
                location                       = data['location'],
                shelf_life                     = data['shelf_life'],
                volume_by_packing              = data['volume_by_packing'],
                base_material_name_and_content = data['base_material_name_and_content'],
                nutrient                       = data['nutrient'],
                gmo                            = data['gmo'],
                import_declaration             = data['import_declaration'],
            )


            # drink_category 테이블
            # drink_category, flag = DrinkCategory.objects.get_or_create(name=data['drink_category'])


            # drink_details 테이블
            drink_detail =DrinkDetail.objects.create(
                product                 = product,
                drink_category          = DrinkCategory.objects.get(name=data['drink_category']),
                alcohol_content         = data['alcohol_content'],
                fragrance               = data['fragrance'],
                flavor                  = data['flavor'],
                finish                  = data['finish'],
                with_who                = data['with_who'],
                what_situation          = data['what_situation'],
                what_mood               = data['what_mood'],
                what_profit             = data['what_profit'],
                recommend_situation     = data['recommend_situation'],
                recommend_eating_method = data['recommend_eating_method'],
                additional_info         = data['additional_info'],
            )


            # taste_matrixs 테이블
            TasteMatrix.objects.create(
                drink_detail       = drink_detail,
                body         = data['taste_body'] if data.get('taste_body') else 0,
                acidity      = data['taste_acidity'] if data.get('taste_acidity') else 0,
                sweetness    = data['taste_sweetness'] if data.get('taste_sweetness') else 0,
                tannin       = data['taste_tannin'] if data.get('taste_tannin') else 0,
                bitter       = data['taste_bitter'] if data.get('taste_bitter') else 0,
                sparkling    = data['taste_sparkling'] if data.get('taste_sparkling') else 0,
                light        = data['taste_light'] if data.get('taste_light') else 0,
                turbidity    = data['taste_turbidity'] if data.get('taste_turbidity') else 0,
                savory       = data['taste_savory'] if data.get('taste_savory') else 0,
                gorgeous     = data['taste_gorgeous'] if data.get('taste_gorgeous') else 0,
                spicy        = data['taste_spicy'] if data.get('taste_spicy') else 0,
            )


            # parings 테이블
            for paring in data['paring']:
                paring, flag = Paring.objects.get_or_create(
                    name        = paring['name'],
                    description = paring['description'],
                )
                drink_detail.drink_detail_paring.add(paring)


            # base_materials 테이블
            for base_material in data['base_material']:
                base_material, flag = BaseMaterial.objects.get_or_create(
                    name = base_material
                )
                drink_detail.drink_detail_base_material.add(base_material)


            # DrinkDetailVolume 테이블
            for volume_and_price in data['volume_and_price']:  # {"volume": "500ml", "price": "500"}

                price = volume_and_price['price']
                volume, flag = Volume.objects.get_or_create(name=volume_and_price['volume'])

                DrinkDetailVolume.objects.get_or_create(
                    drink_detail = drink_detail,
                    volume       = volume,
                    price        = price,
                )

            return JsonResponse({'MESSAGE': 'SUCCESS', 'product_id': product.id}, status=201)

        except IntegrityError as e:
            return JsonResponse({"MESSAGE": "INTEGRITY_ERROR => " + e.args[0]}, status=400)
        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)


    #@signin_decorator
    def delete(self, request, product_id):
        try:
            product_images = ProductImage.objects.filter(product_id=product_id)
            for product_image in product_images:
                filename = product_image.image_url.split('/rip-dev-bucket/')[1]
                response = s3_client.delete_object(
                    Bucket = "rip-dev-bucket",
                    Key    = filename,
                )
                print(f"response: {response}")

            product = Product.objects.get(id=product_id)
            product.delete()

            return JsonResponse({'MESSAGE': 'SUCCESS'}, status=200)

        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
        except Exception as e:
            return JsonResponse({"MESSAGE": "Exception => " + e.args[0]}, status=400)


    @transaction.atomic
    def get(self, request, product_id):
        try:
            product = (Product.objects
                       .select_related('product_category', 'manufacture')
                       .prefetch_related('product_tag',
                                         'productimage_set',
                                         'label_set',
                                         'drinkdetail_set',
                                         'drinkdetail_set__drink_category',
                                         'drinkdetail_set__tastematrix_set',
                                         'drinkdetail_set__drink_detail_paring',
                                         'drinkdetail_set__drink_detail_base_material',
                                         'drinkdetail_set__drinkdetailvolume_set',
                                         'industrialproductinfo_set')
                       .get(id=product_id))

            drink_data = {
                "id"                            : product.id,
                "product_category"              : product.product_category.name,

                "drink_category"                : product.drinkdetail_set.all()[0].drink_category.name,

                "product_image"                 : [{
                                                        "id"       : product_image.id,
                                                        "image_url": product_image.image_url,
                }for product_image in product.productimage_set.all()],

                "label"                         : [{
                                                        "id"       : label.id,
                                                        "image_url": label.image_url,
                }for label in product.label_set.all()],

                "manufacture_name"              : product.manufacture.name,
                "product_name"                  : product.name,
                "subtitle"                      : product.subtitle,
                "price"                         : product.price,
                "content"                       : product.content,
                "is_damhwa_box"                 : product.is_damhwa_box,
                "discount_rate"                 : product.discount_rate,
                "award"                         : product.award,

                "tag"                           : [{
                                                        "id"  : tag.id,
                                                        "name": tag.name,
                }for tag in product.product_tag.all()],

                "food_type"                     : product.industrialproductinfo_set.all()[0].food_type,
                "business_name"                 : product.industrialproductinfo_set.all()[0].business_name,
                "location"                      : product.industrialproductinfo_set.all()[0].location,
                "shelf_life"                    : product.industrialproductinfo_set.all()[0].shelf_life,
                "volume_by_packing"             : product.industrialproductinfo_set.all()[0].volume_by_packing,
                "base_material_name_and_content": product.industrialproductinfo_set.all()[0].base_material_name_and_content,
                "nutrient"                      : product.industrialproductinfo_set.all()[0].nutrient,
                "gmo"                           : product.industrialproductinfo_set.all()[0].gmo,
                "import_declaration"            : product.industrialproductinfo_set.all()[0].import_declaration,

                "alcohol_content"               : product.drinkdetail_set.all()[0].alcohol_content,
                "fragrance"                     : product.drinkdetail_set.all()[0].fragrance,
                "flavor"                        : product.drinkdetail_set.all()[0].flavor,
                "finish"                        : product.drinkdetail_set.all()[0].finish,
                "with_who"                      : product.drinkdetail_set.all()[0].with_who,
                "what_situation"                : product.drinkdetail_set.all()[0].what_situation,
                "what_mood"                     : product.drinkdetail_set.all()[0].what_mood,
                "what_profit"                   : product.drinkdetail_set.all()[0].what_profit,
                "recommend_situation"           : product.drinkdetail_set.all()[0].recommend_situation,
                "recommend_eating_method"       : product.drinkdetail_set.all()[0].recommend_eating_method,
                "additional_info"               : product.drinkdetail_set.all()[0].additional_info,

                "taste_body"                    : product.drinkdetail_set.all()[0].tastematrix_set.all()[0].body,
                "taste_acidity"                 : product.drinkdetail_set.all()[0].tastematrix_set.all()[0].acidity,
                "taste_sweetness"               : product.drinkdetail_set.all()[0].tastematrix_set.all()[0].sweetness,
                "taste_tannin"                  : product.drinkdetail_set.all()[0].tastematrix_set.all()[0].tannin,
                "taste_bitter"                  : product.drinkdetail_set.all()[0].tastematrix_set.all()[0].bitter,
                "taste_sparkling"               : product.drinkdetail_set.all()[0].tastematrix_set.all()[0].sparkling,
                "taste_light"                   : product.drinkdetail_set.all()[0].tastematrix_set.all()[0].light,
                "taste_turbidity"               : product.drinkdetail_set.all()[0].tastematrix_set.all()[0].turbidity,
                "taste_savory"                  : product.drinkdetail_set.all()[0].tastematrix_set.all()[0].savory,
                "taste_gorgeous"                : product.drinkdetail_set.all()[0].tastematrix_set.all()[0].gorgeous,
                "taste_spicy"                   : product.drinkdetail_set.all()[0].tastematrix_set.all()[0].spicy,

                "paring"                        : [{
                                                        "id"         : paring.id,
                                                        "name"       : paring.name,
                                                        "description": paring.description,
                }for paring in product.drinkdetail_set.all()[0].drink_detail_paring.all()],

                "base_material"                 : [{
                                                        "id"  : base_material.id,
                                                        "name": base_material.name,
                }for base_material in product.drinkdetail_set.all()[0].drink_detail_base_material.all()],


                "volume_and_price"              : [{
                                                        "id": volume.volume.id,
                                                        "volume"   : volume.volume.name,
                                                        "price"    : volume.price,
                }for volume in product.drinkdetail_set.all()[0].drinkdetailvolume_set.all()]
            }

            return JsonResponse({'MESSAGE': 'SUCCESS', 'drink_data': drink_data}, status=200)

        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
        except Exception as e:
            return JsonResponse({"MESSAGE": "Exception => " + e.args[0]}, status=400)
