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
from my_settings  import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
from product.utils import s3_client


class PreInfoListView(View):
    # @signin_decorator
    @transaction.atomic
    def get(self, request):
        try:
            pre_info_data = [{
                'brewery': [{
                    'id': brewery.id,
                    'name': brewery.name,
                }for brewery in Manufacture.objects.filter(manufacture_type=ManufactureType.objects.get(name="양조장"))],
                'tag': [{
                    'id': tag.id,
                    'name': tag.name,
                }for tag in Tag.objects.all()],
                'paring': [{
                    'id': paring.id,
                    'name': paring.name,
                }for paring in Paring.objects.all()],
                'base_material': [{
                    'id': base_material.id,
                    'name': base_material.name,
                }for base_material in BaseMaterial.objects.all()],
                'volume': [{
                    'id': volume.id,
                    'name': volume.name,
                }for volume in Volume.objects.all()],
            }]

            return JsonResponse({"MESSAGE": "SUCCESS", "pre_info_data": pre_info_data}, status=200)

        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
