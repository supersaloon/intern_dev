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


    def get(self, request, product_id):
        try:
            product                 = Product.objects.get(id=product_id)
            drink_detail            = (DrinkDetail.objects
                                         .prefetch_related("drinkoption_set__volume")
                                         .get(product_id=product.id))

            drink_data = {
                "id"                            : product.id,
                "product_category"              : product.product_category.name,

                "drink_category"                : drink_detail.drink_category.name,

                "product_image"                 : [{
                                                        "id"       : product_image.id,
                                                        "image_url": product_image.image_url,
                }for product_image in product.productimage_set.all()],

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


                "base_material"                 : [{
                                                        "id"  : base_material.id,
                                                        "name": base_material.name,
                }for base_material in drink_detail.drink_detail_base_material.all()],


                "drink_option"                  : [{
                                                        "id"    : drink_option.volume.id,
                                                        "volume": drink_option.volume.name,
                                                        "price" : drink_option.price,
                                                        "amount": drink_option.amount,
                } for drink_option in drink_detail.drinkoption_set.all()]
            }

            return JsonResponse({'MESSAGE': 'SUCCESS', 'drink_data': drink_data}, status=200)
        except Product.DoesNotExist as e:
            return JsonResponse({"MESSAGE": e.args[0]}, status=400)
        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
        except Exception as e:
            return JsonResponse({"MESSAGE": "Exception => " + str(e)}, status=400)


    @transaction.atomic
    def patch(self, request, product_id):
        try:
            data = json.loads(request.body)

            drink_category, flag    = DrinkCategory.objects.get_or_create(name=data['drink_category'])
            product                 = Product.objects.get(id=product_id)
            drink_detail            = (DrinkDetail.objects
                                         .prefetch_related("drinkoption_set__volume")
                                         .get(product_id=product.id))

            product.name             = data['product_name']
            product.subtitle         = data['subtitle']
            product.price            = data['price']
            product.content          = data['content']
            product.is_damhwa_box    = data['is_damhwa_box']
            product.discount_rate    = data['discount_rate']
            product.award            = data['award']
            product.product_category = ProductCategory.objects.get(name=data['product_category'])
            product.uploader         = Administrator.objects.get(name="homer")
            product.save()

            drink_detail.drink_category = drink_category
            drink_detail.save()


            # product_image
            for product_image in data['product_image']:
                # 사용자가 추가한 이미지를 상품에 연결
                if product_image['status'] == "add":
                    new_product_image = ProductImage.objects.get(id=product_image['id'])
                    new_product_image.product = product
                    new_product_image.save()
                    print(f"신규 이미지: {new_product_image.id} 추가 완료")


            # tag
            for tag in data['tag']:
                # 사용자가 추가한 태그를 추가
                if tag['status'] == "add":
                    new_tag, flag = Tag.objects.get_or_create(name=tag['name'])
                    product.product_tag.add(new_tag)
                    print(f"신규 태그: {new_tag.name} 추가 완료")
                # 사용자가 삭제한 태그를 삭제
                elif tag['status'] == "delete":
                    tag_to_disconnect    = Tag.objects.get(id=tag['id'], name=tag['name'])
                    product_tag_relation = ProductTag.objects.get(tag=tag_to_disconnect, product=product)
                    product_tag_relation.delete()
                    print(f"태그: {tag_to_disconnect.name} 삭제 완료")

                    # 상품과 관계가 제거된 태그의 참조횟수가 0이면 태그 삭제
                    tag_ref_count = ProductTag.objects.filter(tag=tag_to_disconnect).count()
                    print(f'>>>>> ref count of {tag_to_disconnect} is {tag_ref_count}')
                    if tag_ref_count == 0:
                        tag_to_disconnect.delete()


            # base_material
            for base_material in data['base_material']:
                # 사용자가 추가한 원재료를 추가
                if base_material['status'] == "add":
                    new_base_material, flag = BaseMaterial.objects.get_or_create(name=base_material['name'])
                    drink_detail.drink_detail_base_material.add(new_base_material)
                    print(f"신규 원재료: {new_base_material.name} 추가 완료")
                # 사용자가 삭제한 원재료를 삭제
                elif base_material['status'] == "delete":
                    base_material_to_disconnect = BaseMaterial.objects.get(id=base_material['id'], name=base_material['name'])
                    drink_detail_base_material_relation = DrinkDetailBaseMaterial.objects.get(
                        base_material=base_material_to_disconnect,
                        drink_detail=drink_detail)
                    drink_detail_base_material_relation.delete()
                    print(f"원재료: {base_material_to_disconnect.name} 삭제 완료")

                    # 음료 상세와 관계가 제거된 원재료의 참조횟수가 0이면 원재료 삭제
                    base_material_ref_count = DrinkDetailBaseMaterial.objects.filter(base_material=base_material_to_disconnect).count()
                    print(f'>>>>> ref count of {base_material_to_disconnect.name} is {base_material_ref_count}')
                    if base_material_ref_count == 0:
                        base_material_to_disconnect.delete()


            # volume and price
            for drink_option in data['drink_option']:
                '''
                "drink_option":
                [{"id": "32", "volume": "500ml" , "price": "5555" , "status": "add"},
                {"id" : ""  , "volume": "800ml" , "price": "9000" , "status": "delete"},
                {"id" : "40", "volume": "1200ml", "price": "12010", "status": "normal"}],
                '''
                # 사용자가 추가한 용량을 추가
                if drink_option['status'] == "add":
                    new_volume, flag = Volume.objects.get_or_create(name=drink_option['volume'])
                    DrinkOption.objects.create(
                        drink_detail = drink_detail,
                        volume       = new_volume,
                        price        = drink_option['price'],
                        amount       = drink_option['amount'],
                    )
                    print(f"신규 용량: {new_volume.name} 추가 완료")

                # 사용자가 삭제한 용량을 삭제 처리
                elif drink_option['status'] == "delete":
                    volume = Volume.objects.get(id=drink_option['id'], name=drink_option['volume'])
                    drink_option_relation = DrinkOption.objects.get(volume=volume, drink_detail=drink_detail)
                    drink_option_relation.delete()
                    print(f"용량: {volume.name} 삭제 완료")

                    # volume의 참조횟수가 0이면 Volume 자체를 삭제 처리
                    volume_ref_count = DrinkOption.objects.filter(volume=volume).count()
                    print(f'>>>>> ref count of {volume} is {volume_ref_count}')
                    if volume_ref_count == 0:
                        volume.delete()

                elif drink_option['status'] == "normal":
                    # 신규 또는 삭제가 아닌 경우 -> price 덮어쓰기
                    volume = Volume.objects.get(id=drink_option['id'], name=drink_option['volume'])
                    drink_option_relation = DrinkOption.objects.get(volume=volume, drink_detail=drink_detail)
                    drink_option_relation.price = drink_option['price']
                    drink_option_relation.save()


            return JsonResponse({'MESSAGE': 'SUCCESS', 'product_id': product.id}, status=201)

        except IntegrityError as e:
            return JsonResponse({"MESSAGE": "INTEGRITY_ERROR => " + e.args[0]}, status=400)
        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
        except ValueError as e:
            return JsonResponse({"MESSAGE": "VALUE_ERROR => " + e.args[0]}, status=400)
        except ObjectDoesNotExist as e:
            return JsonResponse({"MESSAGE": "ObjectDoesNotExist => " + e.args[0]}, status=400)
