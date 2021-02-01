from django.http  import JsonResponse
from django.views import View
from django.db    import transaction


from product.models import ProductCategory, DrinkCategory, IndustrialProductInfo, Manufacture, ManufactureType, Volume, \
                           Label, TasteMatrix, DrinkDetail, DrinkDetailVolume, Product, Tag, ProductImage, Paring, BaseMaterial


class PreInfoListView(View):
    # @signin_decorator
    @transaction.atomic
    def get(self, request):
        try:
            pre_info_data = {
                'product_category': [{
                    'id'              : product_category.id,
                    'product_category': product_category.name,
                } for product_category in ProductCategory.objects.all()],

                'drink_category'  : [{
                    'id'            : drink_category.id,
                    'drink_category': drink_category.name,
                } for drink_category in DrinkCategory.objects.all()],

                'company_name': [{
                    'id': brewery.id,
                    'company_name': brewery.name,
                }for brewery in Manufacture.objects.filter(manufacture_type=ManufactureType.objects.get(name="양조장"))],

                'tag': [{
                    'value': tag.id,
                    'label': tag.name,
                }for tag in Tag.objects.all()],
                'paring': [{
                    'value': paring.id,
                    'label': paring.name,
                }for paring in Paring.objects.all()],
                'base_material': [{
                    'value': base_material.id,
                    'label': base_material.name,
                }for base_material in BaseMaterial.objects.all()],
                'volume': [{
                    'value': volume.id,
                    'label': volume.name,
                }for volume in Volume.objects.all()],
            }

            return JsonResponse({"MESSAGE": "SUCCESS", "pre_info_data": pre_info_data}, status=200)

        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
