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



class DrinkEvaluationInfoView(View):
    @transaction.atomic
    def post(self, request):
        try:
            data = json.loads(request.body)

            # products 테이블
            product = Product.objects.get(id=data['product_id'])

            # drink_detail 테이블
            drink_detail, flag = DrinkDetail.objects.get_or_create(product=product)
            drink_detail.alcohol_content         = data['alcohol_content'] if data['alcohol_content'] else 0
            drink_detail.fragrance               = data['fragrance']
            drink_detail.flavor                  = data['flavor']
            drink_detail.finish                  = data['finish']
            drink_detail.recommend_situation     = data['recommend_situation']
            drink_detail.recommend_eating_method = data['recommend_eating_method']
            drink_detail.additional_info         = data['additional_info']
            drink_detail.save()


            # taste_matrix 테이블
            taste_matrix, flag = TasteMatrix.objects.get_or_create(drink_detail=drink_detail)
            taste_matrix.body      = data['taste_body'] if data['taste_body'] else 0
            taste_matrix.acidity   = data['taste_acidity'] if data['taste_acidity'] else 0
            taste_matrix.sweetness = data['taste_sweetness'] if data['taste_sweetness'] else 0
            taste_matrix.tannin    = data['taste_tannin'] if data['taste_tannin'] else 0
            taste_matrix.bitter    = data['taste_bitter'] if data['taste_bitter'] else 0
            taste_matrix.sparkling = data['taste_sparkling']if data['taste_sparkling'] else 0
            taste_matrix.light     = data['taste_light'] if data['taste_light'] else 0
            taste_matrix.turbidity = data['taste_turbidity'] if data['taste_turbidity'] else 0
            taste_matrix.savory    = data['taste_savory'] if data['taste_savory'] else 0
            taste_matrix.gorgeous  = data['taste_gorgeous'] if data['taste_gorgeous'] else 0
            taste_matrix.spicy     = data['taste_spicy'] if data['taste_spicy'] else 0
            taste_matrix.save()


            # paring
            for paring in data['paring']:
                paring, flag = Paring.objects.get_or_create(
                    name = paring,
                )
                drink_detail.drink_detail_paring.add(paring)

            return JsonResponse({'MESSAGE': 'SUCCESS', 'product_id': product.id, 'product_name': product.name}, status=201)

        except IntegrityError as e:
            return JsonResponse({"MESSAGE": "INTEGRITY_ERROR => " + e.args[0]}, status=400)
        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
        # except Exception as e:
        #     return JsonResponse({"MESSAGE": "Exception => " + str(e)}, status=400)


    # def get(self, request, product_id):
    #     try:
    #         product = Product.objects.get(id=product_id)
    #         industrial_product_info = IndustrialProductInfo.objects.get(product=product)
    #
    #         drink_industrial_info_data = {
    #             'product_id'                    : product.id,
    #             'product_name'                  : product.name,
    #             'manufacture_name'              : product.manufacture.name,
    #             'food_type'                     : industrial_product_info.food_type,
    #             'business_name'                 : industrial_product_info.business_name,
    #             'location'                      : industrial_product_info.location,
    #             'shelf_life'                    : industrial_product_info.shelf_life,
    #             'volume_by_packing'             : industrial_product_info.volume_by_packing,
    #             'base_material_name_and_content': industrial_product_info.base_material_name_and_content,
    #             'nutrient'                      : industrial_product_info.nutrient,
    #             'gmo'                           : industrial_product_info.gmo,
    #             'import_declaration'            : industrial_product_info.import_declaration,
    #             'label'                         : industrial_product_info.label_url,
    #         }
    #
    #         return JsonResponse({'MESSAGE': 'SUCCESS', 'drink_industrial_info': drink_industrial_info_data}, status=200)
    #     except ObjectDoesNotExist as e:
    #         return JsonResponse({"MESSAGE": "ObjectDoesNotExist => " + e.args[0]}, status=400)
    #     except KeyError as e:
    #         return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
    #     except Exception as e:
    #         return JsonResponse({"MESSAGE": "Exception => " + str(e)}, status=400)
    #
    #
    @transaction.atomic
    def patch(self, request, product_id):
        try:
            data = json.loads(request.body)

            # products 테이블
            product = Product.objects.get(id=product_id)

            # drink_detail 테이블
            drink_detail = DrinkDetail.objects.get(product=product)
            drink_detail.alcohol_content         = data['alcohol_content']
            drink_detail.fragrance               = data['fragrance']
            drink_detail.flavor                  = data['flavor']
            drink_detail.finish                  = data['finish']
            drink_detail.recommend_situation     = data['recommend_situation']
            drink_detail.recommend_eating_method = data['recommend_eating_method']
            drink_detail.additional_info         = data['additional_info']
            drink_detail.save()


            # taste_matrix 테이블
            taste_matrix = TasteMatrix.objects.get(drink_detail=drink_detail)
            taste_matrix.body      = data['taste_body'] if data['taste_body'] else 0
            taste_matrix.acidity   = data['taste_acidity'] if data['taste_acidity'] else 0
            taste_matrix.sweetness = data['taste_sweetness'] if data['taste_sweetness'] else 0
            taste_matrix.tannin    = data['taste_tannin'] if data['taste_tannin'] else 0
            taste_matrix.bitter    = data['taste_bitter'] if data['taste_bitter'] else 0
            taste_matrix.sparkling = data['taste_sparkling']if data['taste_sparkling'] else 0
            taste_matrix.light     = data['taste_light'] if data['taste_light'] else 0
            taste_matrix.turbidity = data['taste_turbidity'] if data['taste_turbidity'] else 0
            taste_matrix.savory    = data['taste_savory'] if data['taste_savory'] else 0
            taste_matrix.gorgeous  = data['taste_gorgeous'] if data['taste_gorgeous'] else 0
            taste_matrix.spicy     = data['taste_spicy'] if data['taste_spicy'] else 0
            taste_matrix.save()


            # paring
            for paring in data['paring']:
                # 사용자가 add한 페어링을 추가
                if paring['status'] == "add":
                    new_paring, flag = Paring.objects.get_or_create(name=paring['name'])
                    drink_detail.drink_detail_paring.add(new_paring)
                    print(f"신규 페어링: {new_paring.name} 추가 완료")
                # 사용자가 delete한 원재료를 삭제
                elif paring['status'] == "delete":
                    paring_to_disconnect = Paring.objects.get(id=paring['id'], name=paring['name'])
                    drink_detail_paring_relation = DrinkDetailParing.objects.get(
                        paring       = paring_to_disconnect,
                        drink_detail = drink_detail)
                    drink_detail_paring_relation.delete()
                    print(f"페어링: {paring_to_disconnect.name} 삭제 완료")

                    # 음료 상세와 관계가 제거된 페어링의 참조횟수가 0이면 페어링 삭제
                    paring_ref_count = DrinkDetailParing.objects.filter(paring=paring_to_disconnect).count()
                    print(f'>>>>> ref count of {paring_to_disconnect.name} is {paring_ref_count}')
                    if paring_ref_count == 0:
                        paring_to_disconnect.delete()


            return JsonResponse({'MESSAGE': 'SUCCESS', 'product_id': product.id, 'product_name': product.name}, status=200)

        except IntegrityError as e:
            return JsonResponse({"MESSAGE": "INTEGRITY_ERROR => " + e.args[0]}, status=400)
        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
        except ValueError as e:
            return JsonResponse({"MESSAGE": "VALUE_ERROR => " + e.args[0]}, status=400)
        except ObjectDoesNotExist as e:
            return JsonResponse({"MESSAGE": "ObjectDoesNotExist => " + e.args[0]}, status=400)
