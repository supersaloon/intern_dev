import boto3
import uuid
import json

from django.http  import JsonResponse
from django.views import View
from django.db    import transaction
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist

from user.models    import Administrator
from product.models import ProductCategory, DrinkCategory, IndustrialProductInfo, Manufacture, ManufactureType, Volume, \
                           Label, TasteMatrix, DrinkDetail, DrinkOption, Product, Tag, ProductImage, Paring, BaseMaterial, \
                            ProductTag, DrinkDetailParing, DrinkDetailBaseMaterial

from product.utils import s3_client, reverse_foreign_key_finder



class DrinkBaseInfoView(View):
    # @signin_decorator
    @transaction.atomic
    def post(self, request):
        try:
            data = json.loads(request.body)
            print("=============================================")
            print(f'data: {data}')

            # product_type -> "주류" 로 하드코딩

            # products 테이블
            product = Product.objects.create(
                name             = data['product_name'],
                subtitle         = data['subtitle'],
                price            = data['price'] if data['price'] else 0,
                content          = data['content'],
                is_damhwa_box    = data['is_damhwa_box'] if data['is_damhwa_box'] else False,
                discount_rate    = data['discount_rate'] if data['discount_rate'] else 0,
                award            = data['award'],
                product_category = ProductCategory.objects.get(name=data['product_category']),
                uploader         = Administrator.objects.get(name="homer"),
            )


            # drink_details 테이블
            drink_detail =DrinkDetail.objects.create(
                product                 = product,
                drink_category          = DrinkCategory.objects.get(name=data['drink_category']),
            )

            # product_image
            if data.get('product_image'):
                for product_image_id in data.get('product_image'):
                    # product_image 에 빈 스트링이 들어오면 for 문 안쪽의 코드가 실행되지 않음
                    product_image         = ProductImage.objects.get(id = product_image_id)
                    product_image.product = product
                    product_image.save()


            # Tag
            if data['tag']:
                for tag in data['tag']:
                    tag, flag = Tag.objects.get_or_create(name=tag)
                    product.product_tag.add(tag)


            # base_materials 테이블
            if data['base_material']:
                for base_material in data['base_material']:
                    base_material, flag = BaseMaterial.objects.get_or_create(
                        name = base_material
                    )
                    drink_detail.drink_detail_base_material.add(base_material)


            # DrinkOption 테이블
            if data['drink_option']:
                for drink_option in data['drink_option']:
                    '''
                    [{"volume": "500ml", "price": "5000", "amount": "1"},
                    {"volume": "700ml", "price": "7000", "amount": "2"},
                    {"volume": "1000ml", "price": "10000", "amount": "3"}]
                    '''
                    price        = drink_option['price']
                    amount       = drink_option['amount']
                    volume, flag = Volume.objects.get_or_create(name=drink_option['volume'])

                    DrinkOption.objects.get_or_create(
                        drink_detail = drink_detail,
                        volume       = volume,
                        price        = price,
                        amount       = amount,
                    )

            return JsonResponse({'MESSAGE': 'SUCCESS', 'product_id': product.id, 'product_name': product.name}, status=201)

        except IntegrityError as e:
            return JsonResponse({"MESSAGE": "INTEGRITY_ERROR => " + e.args[0]}, status=400)
        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
        except Exception as e:
            return JsonResponse({"MESSAGE": "Exception => " + str(e)}, status=400)


    def delete(self, request, product_id):
        try:
            # 상품 이미지 삭제
            product_images = ProductImage.objects.filter(product_id=product_id)
            for product_image in product_images:
                filename = product_image.image_url.split('/rip-dev-bucket/')[1]
                response = s3_client.delete_object(
                    Bucket = "rip-dev-bucket",
                    Key    = filename,
                )
                print(f"response: {response}")

            # 상품 삭제
            product = Product.objects.get(id=product_id)
            product.delete()
            return JsonResponse({'MESSAGE': 'SUCCESS'}, status=200)
        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
        except Exception as e:
            return JsonResponse({"MESSAGE": "Exception => " + e.args[0]}, status=400)
    #
    #
    # @transaction.atomic
    # def get(self, request, product_id):
    #     try:
    #         product                 = Product.objects.get(id=product_id)
    #         drink_detail            = (DrinkDetail.objects
    #                                      .prefetch_related("drinkoption_set__volume")
    #                                      .get(product_id=product.id))
    #         industrial_product_info = product.industrialproductinfo_set.get()
    #         taste_matrix            = drink_detail.tastematrix_set.get()
    #
    #         drink_data = {
    #             "id"                            : product.id,
    #             "product_category"              : product.product_category.name,
    #
    #             "drink_category"                : drink_detail.drink_category.name,
    #
    #             "product_image"                 : [{
    #                                                     "id"       : product_image.id,
    #                                                     "image_url": product_image.image_url,
    #             }for product_image in product.productimage_set.all()],
    #
    #             "label"                         : [{
    #                                                     "id"       : label.id,
    #                                                     "image_url": label.image_url,
    #             }for label in product.label_set.all()],
    #
    #             "manufacture_name"              : product.manufacture.name,
    #             "product_name"                  : product.name,
    #             "subtitle"                      : product.subtitle,
    #             "price"                         : product.price,
    #             "content"                       : product.content,
    #             "is_damhwa_box"                 : product.is_damhwa_box,
    #             "discount_rate"                 : product.discount_rate,
    #             "award"                         : product.award,
    #
    #             "tag"                           : [{
    #                                                     "id"  : tag.id,
    #                                                     "name": tag.name,
    #             }for tag in product.product_tag.all()],
    #
    #             "food_type"                     : industrial_product_info.food_type,
    #             "business_name"                 : industrial_product_info.business_name,
    #             "location"                      : industrial_product_info.location,
    #             "shelf_life"                    : industrial_product_info.shelf_life,
    #             "volume_by_packing"             : industrial_product_info.volume_by_packing,
    #             "base_material_name_and_content": industrial_product_info.base_material_name_and_content,
    #             "nutrient"                      : industrial_product_info.nutrient,
    #             "gmo"                           : industrial_product_info.gmo,
    #             "import_declaration"            : industrial_product_info.import_declaration,
    #
    #             "alcohol_content"               : drink_detail.alcohol_content,
    #             "fragrance"                     : drink_detail.fragrance,
    #             "flavor"                        : drink_detail.flavor,
    #             "finish"                        : drink_detail.finish,
    #             "with_who"                      : drink_detail.with_who,
    #             "what_situation"                : drink_detail.what_situation,
    #             "what_mood"                     : drink_detail.what_mood,
    #             "what_profit"                   : drink_detail.what_profit,
    #             "recommend_situation"           : drink_detail.recommend_situation,
    #             "recommend_eating_method"       : drink_detail.recommend_eating_method,
    #             "additional_info"               : drink_detail.additional_info,
    #
    #             "taste_body"                    : taste_matrix.body,
    #             "taste_acidity"                 : taste_matrix.acidity,
    #             "taste_sweetness"               : taste_matrix.sweetness,
    #             "taste_tannin"                  : taste_matrix.tannin,
    #             "taste_bitter"                  : taste_matrix.bitter,
    #             "taste_sparkling"               : taste_matrix.sparkling,
    #             "taste_light"                   : taste_matrix.light,
    #             "taste_turbidity"               : taste_matrix.turbidity,
    #             "taste_savory"                  : taste_matrix.savory,
    #             "taste_gorgeous"                : taste_matrix.gorgeous,
    #             "taste_spicy"                   : taste_matrix.spicy,
    #
    #             "paring"                        : [{
    #                                                     "id"         : paring.id,
    #                                                     "name"       : paring.name,
    #             }for paring in drink_detail.drink_detail_paring.all()],
    #
    #             "base_material"                 : [{
    #                                                     "id"  : base_material.id,
    #                                                     "name": base_material.name,
    #             }for base_material in drink_detail.drink_detail_base_material.all()],
    #
    #
    #             "drink_option"                  : [{
    #                                                     "id"    : drink_option.volume.id,
    #                                                     "volume": drink_option.volume.name,
    #                                                     "price" : drink_option.price,
    #                                                     "amount": drink_option.amount,
    #             } for drink_option in drink_detail.drinkoption_set.all()]
    #         }
    #
    #         return JsonResponse({'MESSAGE': 'SUCCESS', 'drink_data': drink_data}, status=200)
    #     except Product.DoesNotExist as e:
    #         return JsonResponse({"MESSAGE": e.args[0]}, status=400)
    #     except KeyError as e:
    #         return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
    #     except Exception as e:
    #         return JsonResponse({"MESSAGE": "Exception => " + str(e)}, status=400)
    #
    #
    # @transaction.atomic
    # def patch(self, request, product_id):
    #     try:
    #         data = json.loads(request.body)
    #
    #         drink_category, flag    = DrinkCategory.objects.get_or_create(name=data['drink_category'])
    #         product                 = Product.objects.get(id=product_id)
    #         drink_detail            = (DrinkDetail.objects
    #                                      .prefetch_related("drinkoption_set__volume")
    #                                      .get(product_id=product.id))
    #         industrial_product_info = product.industrialproductinfo_set.get()
    #         taste_matrix            = drink_detail.tastematrix_set.get()
    #
    #         product.name             = data['product_name']
    #         product.subtitle         = data['subtitle']
    #         product.price            = data['price']
    #         product.content          = data['content']
    #         product.is_damhwa_box    = data['is_damhwa_box']
    #         product.discount_rate    = data['discount_rate']
    #         product.award            = data['award']
    #         product.product_category = ProductCategory.objects.get(name=data['product_category'])
    #         product.manufacture      = Manufacture.objects.get(name=data['manufacture_name'])
    #         product.uploader         = Administrator.objects.get(name   = "homer")
    #         product.save()
    #
    #
    #         # product_image
    #         for product_image in data['product_image']:
    #             # 사용자가 추가한 이미지를 상품에 연결
    #             if product_image['status'] == "add":
    #                 new_product_image = ProductImage.objects.get(id=product_image['id'])
    #                 new_product_image.product = product
    #                 new_product_image.save()
    #                 print(f"신규 이미지: {new_product_image.id} 추가 완료")
    #
    #
    #         for label in data['label']:
    #             # 사용자가 추가한 이미지를 상품에 연결
    #             if label['status'] == "add":
    #                 new_label = Label.objects.get(id=label['id'])
    #                 new_label.product = product
    #                 new_label.save()
    #                 print(f"신규 라벨: {new_label.id} 추가 완료")
    #
    #
    #         # tag
    #         for tag in data['tag']:
    #             # 사용자가 추가한 태그를 추가
    #             if tag['status'] == "add":
    #                 new_tag, flag = Tag.objects.get_or_create(name=tag['name'])
    #                 product.product_tag.add(new_tag)
    #                 print(f"신규 태그: {new_tag.name} 추가 완료")
    #             # 사용자가 삭제한 태그를 삭제
    #             elif tag['status'] == "delete":
    #                 tag_to_disconnect    = Tag.objects.get(id=tag['id'], name=tag['name'])
    #                 product_tag_relation = ProductTag.objects.get(tag=tag_to_disconnect, product=product)
    #                 product_tag_relation.delete()
    #                 print(f"태그: {tag_to_disconnect.name} 삭제 완료")
    #
    #                 # 상품과 관계가 제거된 태그의 참조횟수가 0이면 태그 삭제
    #                 tag_ref_count = ProductTag.objects.filter(tag=tag_to_disconnect).count()
    #                 print(f'>>>>> ref count of {tag_to_disconnect} is {tag_ref_count}')
    #                 if tag_ref_count == 0:
    #                     tag_to_disconnect.delete()
    #
    #
    #         # base_material
    #         for base_material in data['base_material']:
    #             # 사용자가 추가한 원재료를 추가
    #             if base_material['status'] == "add":
    #                 new_base_material, flag = BaseMaterial.objects.get_or_create(name=base_material['name'])
    #                 drink_detail.drink_detail_base_material.add(new_base_material)
    #                 print(f"신규 원재료: {new_base_material.name} 추가 완료")
    #             # 사용자가 삭제한 원재료를 삭제
    #             elif base_material['status'] == "delete":
    #                 base_material_to_disconnect = BaseMaterial.objects.get(id=base_material['id'], name=base_material['name'])
    #                 drink_detail_base_material_relation = DrinkDetailBaseMaterial.objects.get(
    #                     base_material=base_material_to_disconnect,
    #                     drink_detail=drink_detail)
    #                 drink_detail_base_material_relation.delete()
    #                 print(f"원재료: {base_material_to_disconnect.name} 삭제 완료")
    #
    #                 # 음료 상세와 관계가 제거된 원재료의 참조횟수가 0이면 원재료 삭제
    #                 base_material_ref_count = DrinkDetailBaseMaterial.objects.filter(base_material=base_material_to_disconnect).count()
    #                 print(f'>>>>> ref count of {base_material_to_disconnect.name} is {base_material_ref_count}')
    #                 if base_material_ref_count == 0:
    #                     base_material_to_disconnect.delete()
    #
    #
    #         # paring
    #         for paring in data['paring']:
    #             # 사용자가 추가한 페어링을 추가
    #             if paring['status'] == "add":
    #                 new_paring, flag = Paring.objects.get_or_create(name=paring['name'])
    #                 drink_detail.drink_detail_paring.add(new_paring)
    #                 print(f"신규 페어링: {new_paring.name} 추가 완료")
    #             # 사용자가 삭제한 페어링을 삭제
    #             elif paring['status'] == "delete":
    #                 paring_to_disconnect         = Paring.objects.get(id=paring['id'], name=paring['name'])
    #                 drink_detail_paring_relation = DrinkDetailParing.objects.get(paring=paring_to_disconnect, drink_detail=drink_detail)
    #                 drink_detail_paring_relation.delete()
    #                 print(f"페어링: {paring_to_disconnect.name} 삭제 완료")
    #
    #                 # 음료 상세와 관계가 제거된 페어링의 참조횟수가 0이면 페어링 삭제
    #                 paring_ref_count = DrinkDetailParing.objects.filter(paring=paring_to_disconnect).count()
    #                 print(f'>>>>> ref count of {paring_to_disconnect} is {paring_ref_count}')
    #                 if paring_ref_count == 0:
    #                     paring_to_disconnect.delete()
    #
    #
    #         # volume and price
    #         for drink_option in data['drink_option']:
    #             '''
    #             "drink_option":
    #             [{"id": "32", "volume": "500ml" , "price": "5555" , "status": "add"},
    #             {"id" : ""  , "volume": "800ml" , "price": "9000" , "status": "delete"},
    #             {"id" : "40", "volume": "1200ml", "price": "12010", "status": "normal"}],
    #             '''
    #             # 사용자가 추가한 용량을 추가
    #             if drink_option['status'] == "add":
    #                 new_volume, flag = Volume.objects.get_or_create(name=drink_option['volume'])
    #                 DrinkOption.objects.create(
    #                     drink_detail = drink_detail,
    #                     volume       = new_volume,
    #                     price        = drink_option['price'],
    #                     amount       = drink_option['amount'],
    #                 )
    #                 print(f"신규 용량: {new_volume.name} 추가 완료")
    #
    #             # 사용자가 삭제한 용량을 삭제 처리
    #             elif drink_option['status'] == "delete":
    #                 volume = Volume.objects.get(id=drink_option['id'], name=drink_option['volume'])
    #                 drink_option_relation = DrinkOption.objects.get(volume=volume, drink_detail=drink_detail)
    #                 drink_option_relation.delete()
    #                 print(f"용량: {volume.name} 삭제 완료")
    #
    #                 # volume의 참조횟수가 0이면 Volume 자체를 삭제 처리
    #                 volume_ref_count = DrinkOption.objects.filter(volume=volume).count()
    #                 print(f'>>>>> ref count of {volume} is {volume_ref_count}')
    #                 if volume_ref_count == 0:
    #                     volume.delete()
    #
    #             elif drink_option['status'] == "normal":
    #                 # 신규 또는 삭제가 아닌 경우 -> price 덮어쓰기
    #                 volume = Volume.objects.get(id=drink_option['id'], name=drink_option['volume'])
    #                 drink_option_relation = DrinkOption.objects.get(volume=volume, drink_detail=drink_detail)
    #                 drink_option_relation.price = drink_option['price']
    #                 drink_option_relation.save()
    #
    #
    #         # industrial_product_infos 테이블
    #         industrial_product_info.food_type                      = data['food_type']
    #         industrial_product_info.business_name                  = data['business_name']
    #         industrial_product_info.location                       = data['location']
    #         industrial_product_info.shelf_life                     = data['shelf_life']
    #         industrial_product_info.volume_by_packing              = data['volume_by_packing']
    #         industrial_product_info.base_material_name_and_content = data['base_material_name_and_content']
    #         industrial_product_info.nutrient                       = data['nutrient']
    #         industrial_product_info.gmo                            = data['gmo']
    #         industrial_product_info.import_declaration             = data['import_declaration']
    #         industrial_product_info.save()
    #
    #
    #         # # drink_details 테이블
    #         drink_detail.product                 = product
    #         drink_detail.drink_category          = DrinkCategory.objects.get(name=data['drink_category'])
    #         drink_detail.alcohol_content         = data['alcohol_content']
    #         drink_detail.fragrance               = data['fragrance']
    #         drink_detail.flavor                  = data['flavor']
    #         drink_detail.finish                  = data['finish']
    #         drink_detail.with_who                = data['with_who']
    #         drink_detail.what_situation          = data['what_situation']
    #         drink_detail.what_mood               = data['what_mood']
    #         drink_detail.what_profit             = data['what_profit']
    #         drink_detail.recommend_situation     = data['recommend_situation']
    #         drink_detail.recommend_eating_method = data['recommend_eating_method']
    #         drink_detail.additional_info         = data['additional_info']
    #         drink_detail.save()
    #
    #
    #         # taste_matrixs 테이블
    #         taste_matrix.body         = data['taste_body'] if data.get('taste_body') else 0
    #         taste_matrix.acidity      = data['taste_acidity'] if data.get('taste_acidity') else 0
    #         taste_matrix.sweetness    = data['taste_sweetness'] if data.get('taste_sweetness') else 0
    #         taste_matrix.tannin       = data['taste_tannin'] if data.get('taste_tannin') else 0
    #         taste_matrix.bitter       = data['taste_bitter'] if data.get('taste_bitter') else 0
    #         taste_matrix.sparkling    = data['taste_sparkling'] if data.get('taste_sparkling') else 0
    #         taste_matrix.light        = data['taste_light'] if data.get('taste_light') else 0
    #         taste_matrix.turbidity    = data['taste_turbidity'] if data.get('taste_turbidity') else 0
    #         taste_matrix.savory       = data['taste_savory'] if data.get('taste_savory') else 0
    #         taste_matrix.gorgeous     = data['taste_gorgeous'] if data.get('taste_gorgeous') else 0
    #         taste_matrix.spicy        = data['taste_spicy'] if data.get('taste_spicy') else 0
    #         taste_matrix.save()
    #
    #
    #         return JsonResponse({'MESSAGE': 'SUCCESS', 'product_id': product.id}, status=201)
    #
    #     except IntegrityError as e:
    #         return JsonResponse({"MESSAGE": "INTEGRITY_ERROR => " + e.args[0]}, status=400)
    #     except KeyError as e:
    #         return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
    #     except ValueError as e:
    #         return JsonResponse({"MESSAGE": "VALUE_ERROR => " + e.args[0]}, status=400)
    #     except ObjectDoesNotExist as e:
    #         return JsonResponse({"MESSAGE": "ObjectDoesNotExist => " + e.args[0]}, status=400)