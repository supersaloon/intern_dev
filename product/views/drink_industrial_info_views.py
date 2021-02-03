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



class DrinkIndustrialInfoView(View):
    @transaction.atomic
    def post(self, request):
        try:
            data = json.loads(request.body)
            print("=============================================")
            print(f'data: {data}')

            # products 테이블
            product = Product.objects.get(id=data['product_id'])

            # manufacture 테이블
            if data['manufacture_name']:
                manufacture = Manufacture.objects.get(name=data['manufacture_name'])
                product.manufacture = manufacture
                product.save()

            # industrial_product_info 테이블
            industrial_product_info = IndustrialProductInfo.objects.get_or_create(product=product)

            industrial_product_info.food_type = data['food_type']
            industrial_product_info.business_name = data['business_name']
            industrial_product_info.location = data['location']
            industrial_product_info.shelf_life = data['shelf_life']
            industrial_product_info.volume_by_packing = data['volume_by_packing']
            industrial_product_info.base_material_name_and_content = data['base_material_name_and_content']
            industrial_product_info.nutrient = data['nutrient']
            industrial_product_info.gmo = data['gmo']
            industrial_product_info.import_declaration = data['import_declaration']
            industrial_product_info.label_url = data['label']
            industrial_product_info.save()

            return JsonResponse({'MESSAGE': 'SUCCESS', 'product_id': product.id, 'product_name': product.name}, status=201)

        except IntegrityError as e:
            return JsonResponse({"MESSAGE": "INTEGRITY_ERROR => " + e.args[0]}, status=400)
        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
        except Exception as e:
            return JsonResponse({"MESSAGE": "Exception => " + str(e)}, status=400)


    def get(self, request, product_id):
        try:
            product = Product.objects.get(id=product_id)
            industrial_product_info = IndustrialProductInfo.objects.get(product=product)

            drink_industrial_info_data = {
                'product_id'                    : product.id,
                'product_name'                  : product.name,
                'manufacture_name'              : product.manufacture.name,
                'food_type'                     : industrial_product_info.food_type,
                'business_name'                 : industrial_product_info.business_name,
                'location'                      : industrial_product_info.location,
                'shelf_life'                    : industrial_product_info.shelf_life,
                'volume_by_packing'             : industrial_product_info.volume_by_packing,
                'base_material_name_and_content': industrial_product_info.base_material_name_and_content,
                'nutrient'                      : industrial_product_info.nutrient,
                'gmo'                           : industrial_product_info.gmo,
                'import_declaration'            : industrial_product_info.import_declaration,
                'label'                         : industrial_product_info.label_url,
            }

            return JsonResponse({'MESSAGE': 'SUCCESS', 'drink_industrial_info': drink_industrial_info_data}, status=200)
        except ObjectDoesNotExist as e:
            return JsonResponse({"MESSAGE": "ObjectDoesNotExist => " + e.args[0]}, status=400)
        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
        # except Exception as e:
        #     return JsonResponse({"MESSAGE": "Exception => " + str(e)}, status=400)
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
    #
    #         product.name             = data['product_name']
    #         product.subtitle         = data['subtitle']
    #         product.price            = data['price']
    #         product.content          = data['content']
    #         product.is_damhwa_box    = data['is_damhwa_box']
    #         product.discount_rate    = data['discount_rate']
    #         product.award            = data['award']
    #         product.product_category = ProductCategory.objects.get(name=data['product_category'])
    #         product.uploader         = Administrator.objects.get(name="homer")
    #         product.save()
    #
    #         drink_detail.drink_category = drink_category
    #         drink_detail.save()
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
