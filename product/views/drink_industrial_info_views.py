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

            # products 테이블
            product = Product.objects.get(id=data['product_id'])

            # manufacture 테이블
            if data['manufacture_name']:
                manufacture = Manufacture.objects.get(name=data['manufacture_name'])
                product.manufacture = manufacture
                product.save()

            # industrial_product_info 테이블
            industrial_product_info, flag = IndustrialProductInfo.objects.get_or_create(product=product)

            industrial_product_info.food_type                      = data['food_type']
            industrial_product_info.business_name                  = data['business_name']
            industrial_product_info.location                       = data['location']
            industrial_product_info.shelf_life                     = data['shelf_life']
            industrial_product_info.volume_by_packing              = data['volume_by_packing']
            industrial_product_info.base_material_name_and_content = data['base_material_name_and_content']
            industrial_product_info.nutrient                       = data['nutrient']
            industrial_product_info.gmo                            = data['gmo']
            industrial_product_info.import_declaration             = data['import_declaration']
            industrial_product_info.label_url                      = data['label']
            industrial_product_info.save()

            return JsonResponse({'MESSAGE': 'SUCCESS', 'product_id': product.id, 'product_name': product.name}, status=201)

        except IntegrityError as e:
            return JsonResponse({"MESSAGE": "INTEGRITY_ERROR => " + e.args[0]}, status=400)
        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
        # except Exception as e:
        #     return JsonResponse({"MESSAGE": "Exception => " + str(e)}, status=400)


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
        except Exception as e:
            return JsonResponse({"MESSAGE": "Exception => " + str(e)}, status=400)


    @transaction.atomic
    def patch(self, request, product_id):
        try:
            data = json.loads(request.body)

            # products 테이블
            product = Product.objects.get(id=data['product_id'])

            # manufacture 테이블
            if data['manufacture_name']:
                manufacture = Manufacture.objects.get(name=data['manufacture_name'])
                product.manufacture = manufacture
                product.save()

            # industrial_product_info 테이블
            industrial_product_info = IndustrialProductInfo.objects.get(product=product)

            industrial_product_info.food_type                      = data['food_type']
            industrial_product_info.business_name                  = data['business_name']
            industrial_product_info.location                       = data['location']
            industrial_product_info.shelf_life                     = data['shelf_life']
            industrial_product_info.volume_by_packing              = data['volume_by_packing']
            industrial_product_info.base_material_name_and_content = data['base_material_name_and_content']
            industrial_product_info.nutrient                       = data['nutrient']
            industrial_product_info.gmo                            = data['gmo']
            industrial_product_info.import_declaration             = data['import_declaration']
            industrial_product_info.label_url                      = data['label']
            industrial_product_info.save()

            return JsonResponse({'MESSAGE': 'SUCCESS', 'product_id': product.id}, status=200)

        except IntegrityError as e:
            return JsonResponse({"MESSAGE": "INTEGRITY_ERROR => " + e.args[0]}, status=400)
        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
        except ValueError as e:
            return JsonResponse({"MESSAGE": "VALUE_ERROR => " + e.args[0]}, status=400)
        except ObjectDoesNotExist as e:
            return JsonResponse({"MESSAGE": "ObjectDoesNotExist => " + e.args[0]}, status=400)
