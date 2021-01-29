import boto3
import uuid
import json

from django.http  import JsonResponse
from django.views import View
from django.db    import transaction
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from django.http import Http404

from user.models    import Administrator
from product.models import ProductCategory, DrinkCategory, IndustrialProductInfo, Manufacture, ManufactureType, Volume, \
                           Label, TasteMatrix, DrinkDetail, DrinkDetailVolume, Product, Tag, ProductImage, Paring, BaseMaterial, \
                            ProductTag

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
                # product_image 에 빈 스트링이 들어오면 for 문 안쪽의 코드가 실행되지 않음
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
                drink_detail = drink_detail,
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
        except Exception as e:
            return JsonResponse({"MESSAGE": "Exception => " + e.args[0]}, status=400)


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
            product                 = Product.objects.get(id=product_id)
            drink_detail            = (DrinkDetail.objects
                                         .prefetch_related("drinkdetailvolume_set__volume")
                                         .get(product_id=product.id))
            industrial_product_info = product.industrialproductinfo_set.get()
            taste_matrix            = drink_detail.tastematrix_set.get()

            drink_data = {
                "id"                            : product.id,
                "product_category"              : product.product_category.name,

                "drink_category"                : drink_detail.drink_category.name,

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

                "food_type"                     : industrial_product_info.food_type,
                "business_name"                 : industrial_product_info.business_name,
                "location"                      : industrial_product_info.location,
                "shelf_life"                    : industrial_product_info.shelf_life,
                "volume_by_packing"             : industrial_product_info.volume_by_packing,
                "base_material_name_and_content": industrial_product_info.base_material_name_and_content,
                "nutrient"                      : industrial_product_info.nutrient,
                "gmo"                           : industrial_product_info.gmo,
                "import_declaration"            : industrial_product_info.import_declaration,

                "alcohol_content"               : drink_detail.alcohol_content,
                "fragrance"                     : drink_detail.fragrance,
                "flavor"                        : drink_detail.flavor,
                "finish"                        : drink_detail.finish,
                "with_who"                      : drink_detail.with_who,
                "what_situation"                : drink_detail.what_situation,
                "what_mood"                     : drink_detail.what_mood,
                "what_profit"                   : drink_detail.what_profit,
                "recommend_situation"           : drink_detail.recommend_situation,
                "recommend_eating_method"       : drink_detail.recommend_eating_method,
                "additional_info"               : drink_detail.additional_info,

                "taste_body"                    : taste_matrix.body,
                "taste_acidity"                 : taste_matrix.acidity,
                "taste_sweetness"               : taste_matrix.sweetness,
                "taste_tannin"                  : taste_matrix.tannin,
                "taste_bitter"                  : taste_matrix.bitter,
                "taste_sparkling"               : taste_matrix.sparkling,
                "taste_light"                   : taste_matrix.light,
                "taste_turbidity"               : taste_matrix.turbidity,
                "taste_savory"                  : taste_matrix.savory,
                "taste_gorgeous"                : taste_matrix.gorgeous,
                "taste_spicy"                   : taste_matrix.spicy,

                "paring"                        : [{
                                                        "id"         : paring.id,
                                                        "name"       : paring.name,
                                                        "description": paring.description,
                }for paring in drink_detail.drink_detail_paring.all()],

                "base_material"                 : [{
                                                        "id"  : base_material.id,
                                                        "name": base_material.name,
                }for base_material in drink_detail.drink_detail_base_material.all()],


                "volume_and_price"              : [{
                                                        "id"    : volume.volume.id,
                                                        "volume": volume.volume.name,
                                                        "price" : volume.price,
                } for volume in drink_detail.drinkdetailvolume_set.all()]
            }

            return JsonResponse({'MESSAGE': 'SUCCESS', 'drink_data': drink_data}, status=200)
        except Product.DoesNotExist as e:
            return JsonResponse({"MESSAGE": e.args[0]}, status=400)
        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
        except Exception as e:
            return JsonResponse({"MESSAGE": "Exception => " + e.args[0]}, status=400)


    @transaction.atomic
    def patch(self, request, product_id):
        try:
            data = json.loads(request.body)

            product                 = Product.objects.get(id=product_id)
            drink_detail            = (DrinkDetail.objects
                                         .prefetch_related("drinkdetailvolume_set__volume")
                                         .get(product_id=product.id))
            industrial_product_info = product.industrialproductinfo_set.get()
            taste_matrix            = drink_detail.tastematrix_set.get()

            product.name             = data['product_name']
            product.subtitle         = data['subtitle']
            product.price            = data['price']
            product.content          = data['content']
            product.is_damhwa_box    = data['is_damhwa_box']
            product.discount_rate    = data['discount_rate']
            product.award            = data['award']
            product.product_category = ProductCategory.objects.get(name=data['product_category'])
            product.manufacture      = Manufacture.objects.get(name=data['manufacture_name'])
            product.uploader         = Administrator.objects.get(name   = "homer")
            product.save()


            # # product_image
            # for product_image_id in data['product_image']:
            #     # product_image 에 빈 스트링이 들어오면 for 문 안쪽의 코드가 실행되지 않음
            #     product_image = ProductImage.objects.get(id=product_image_id)
            #     product_image.product = product
            #     product_image.save()
            #
            #
            # # label
            # for label_id in data['label']:
            #     label = Label.objects.get(id=label_id)
            #     label.product = product
            #     label.save()
            #
            #
            # 삭제된 태그가 있는지 확인 -> 삭제되었으면 관계 끊기
            # 삭제된 대그의 참조 횟수가 0인지 확인 -> 0이면 태그를 테이블에서 삭제
            tags_to_delete = []

            existing_tags = [tag.name for tag in product.product_tag.all()]
            print("=============================")
            print(existing_tags)  # ['휴가', '휴가', '혼맥', '치맥']
            print("=============================")
            # 기존 태그 확인
            for tag in data['tag']:
                print(f'tag: {tag}')
                if tag in existing_tags:
                    existing_tags.remove(tag)
                    print(f'existing_tags: {existing_tags}')
                # 신규 태그 추가
                new_tag, flag = Tag.objects.get_or_create(name=tag)
                product.product_tag.add(new_tag)
                print(f"신규 태그: {new_tag.name} 추가 완료")

            # 삭제된 태그 관계 제거
            for tag in existing_tags:
                product_tag_relation = ProductTag.objects.get(tag=Tag.objects.get(name=tag), product=product)
                product_tag_relation.delete()




            # tag 삭제 -> delete 로 날리면 중간테이블 ,tag 테이블에서 모두 날아감


            # industrial_product_infos 테이블
            industrial_product_info.food_type                      = data['food_type']
            industrial_product_info.business_name                  = data['business_name']
            industrial_product_info.location                       = data['location']
            industrial_product_info.shelf_life                     = data['shelf_life']
            industrial_product_info.volume_by_packing              = data['volume_by_packing']
            industrial_product_info.base_material_name_and_content = data['base_material_name_and_content']
            industrial_product_info.nutrient                       = data['nutrient']
            industrial_product_info.gmo                            = data['gmo']
            industrial_product_info.import_declaration             = data['import_declaration']
            industrial_product_info.save()


            # drink_category 테이블
            drink_category, flag = DrinkCategory.objects.get_or_create(name=data['drink_category'])


            # # drink_details 테이블
            drink_detail.product                 = product
            drink_detail.drink_category          = DrinkCategory.objects.get(name=data['drink_category'])
            drink_detail.alcohol_content         = data['alcohol_content']
            drink_detail.fragrance               = data['fragrance']
            drink_detail.flavor                  = data['flavor']
            drink_detail.finish                  = data['finish']
            drink_detail.with_who                = data['with_who']
            drink_detail.what_situation          = data['what_situation']
            drink_detail.what_mood               = data['what_mood']
            drink_detail.what_profit             = data['what_profit']
            drink_detail.recommend_situation     = data['recommend_situation']
            drink_detail.recommend_eating_method = data['recommend_eating_method']
            drink_detail.additional_info         = data['additional_info']


            # taste_matrixs 테이블
            taste_matrix.body         = data['taste_body'] if data.get('taste_body') else 0
            taste_matrix.acidity      = data['taste_acidity'] if data.get('taste_acidity') else 0
            taste_matrix.sweetness    = data['taste_sweetness'] if data.get('taste_sweetness') else 0
            taste_matrix.tannin       = data['taste_tannin'] if data.get('taste_tannin') else 0
            taste_matrix.bitter       = data['taste_bitter'] if data.get('taste_bitter') else 0
            taste_matrix.sparkling    = data['taste_sparkling'] if data.get('taste_sparkling') else 0
            taste_matrix.light        = data['taste_light'] if data.get('taste_light') else 0
            taste_matrix.turbidity    = data['taste_turbidity'] if data.get('taste_turbidity') else 0
            taste_matrix.savory       = data['taste_savory'] if data.get('taste_savory') else 0
            taste_matrix.gorgeous     = data['taste_gorgeous'] if data.get('taste_gorgeous') else 0
            taste_matrix.spicy        = data['taste_spicy'] if data.get('taste_spicy') else 0
            #
            #
            # # parings 테이블
            # for paring in data['paring']:
            #     paring, flag = Paring.objects.get_or_create(
            #         name        = paring['name'],
            #         description = paring['description'],
            #     )
            #     drink_detail.drink_detail_paring.add(paring)
            #
            #
            # # base_materials 테이블
            # for base_material in data['base_material']:
            #     base_material, flag = BaseMaterial.objects.get_or_create(
            #         name = base_material
            #     )
            #     drink_detail.drink_detail_base_material.add(base_material)
            #
            #
            # # DrinkDetailVolume 테이블
            # for volume_and_price in data['volume_and_price']:  # {"volume": "500ml", "price": "500"}
            #
            #     price = volume_and_price['price']
            #     volume, flag = Volume.objects.get_or_create(name=volume_and_price['volume'])
            #
            #     DrinkDetailVolume.objects.get_or_create(
            #         drink_detail = drink_detail,
            #         volume       = volume,
            #         price        = price,
            #     )

            return JsonResponse({'MESSAGE': 'SUCCESS', 'product_id': product.id}, status=201)

        except IntegrityError as e:
            return JsonResponse({"MESSAGE": "INTEGRITY_ERROR => " + e.args[0]}, status=400)
        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
        except Exception as e:
            return JsonResponse({"MESSAGE": "Exception => " + str(e)}, status=400)
