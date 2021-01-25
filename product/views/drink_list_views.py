import boto3
import uuid
import json

from django.http  import JsonResponse
from django.views import View
from django.db    import transaction
from django.db.utils import IntegrityError

from user.models    import Administrator
from product.models import ProductCategory, DrinkCategory, IndustrialProductInfo, Manufacture, \
                           Label, TasteMatrix, DrinkDetail, DrinkDetailVolume, Product, Tag, ProductImage, Paring, DrinkDetailParing
from product.utils import reverse_foreign_key_finder


class DrinkListView(View):
    # @signin_decorator
    @transaction.atomic
    def get(self, request):

        offset = int(request.GET.get('offset', 0))
        limit  = int(request.GET.get('limit', 10))
        limit += offset

        try:
            # reverse_foreign_key_finder(Product)
            """
            ProductTag      product producttag_set
            ProductImage    product productimage_set
            IndustrialProductInfo   product industrialproductinfo_set
            Label   product label_set
            DrinkDetail     product drinkdetail_set
            """

            products = Product.objects\
                .select_related('product_category', 'manufacture')\
                .prefetch_related('productimage_set',  'drinkdetail_set', 'drinkdetail_set__drink_category')\
                .order_by('-created_at')\
                .all()

            drink_data = [{
                'id' : product.id,
                'product_image': [{
                    'id'       : product_image.id,
                    'image_url': product_image.image_url,
                }for product_image in product.productimage_set.all()],
                'product_category': product.product_category.name,
                'drink_category': product.drinkdetail_set.all()[0].drink_category.name,
                'brewery': product.manufacture.name,
                'product_name' : product.name,
                'price'        : product.price,
                'discount_rate': product.discount_rate,
                'create_at'    : product.created_at
            }for product in products][offset:limit]

            return JsonResponse({'MESSAGE': 'SUCCESS', "drink_data": drink_data}, status=200)

        except IntegrityError as e:
            return JsonResponse({"MESSAGE": "INTEGRITY_ERROR => " + e.args[0]}, status=400)
        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
