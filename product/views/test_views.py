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
                           Label, TasteMatrix, DrinkDetail, DrinkOption, Product, Tag, ProductImage, Paring, BaseMaterial
from product.utils import s3_client, reverse_foreign_key_finder


class TestView(View):
    @transaction.atomic
    def get(self, request, id):
        try:
            # product = (Product.objects
            #            .prefetch_related('product_tag')
            #            .get(id=id))

            data = {}
            print("===== 쿼리 시작 =====")
            product = Product.objects.get(id=id)
            print("===== 테스트 시작 =====")
            print(product.subtitle)
            print(product.price)


            for tag in product.product_tag.all():
                # tag.name = "휴가"
                # tag.save()
                print(tag.name)


            # print("===== 그냥 데이터 가져오기 =====")
            # # for tag in product.product_tag
            #     print(tag.name)


            # drink_data = {
            #     "tag"                           : [{
            #                                             "id"  : tag.id,
            #                                             "name": tag.name,
            #     }for tag in product.product_tag.all()],
            #
            # }

            return JsonResponse({'MESSAGE': 'SUCCESS', 'data': data}, status=200)
        except Product.DoesNotExist as e:
            return JsonResponse({"MESSAGE": e.args[0]}, status=400)
        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
        except Exception as e:
            return JsonResponse({"MESSAGE": "Exception => " + e.args[0]}, status=400)
