import boto3
import uuid
import json

from django.http     import JsonResponse
from django.views    import View
from django.db       import transaction
from django.db.utils import IntegrityError

from user.models    import Administrator
from product.models import Product


class DrinkListView(View):
    # @signin_decorator
    @transaction.atomic
    def get(self, request):

        offset = int(request.GET.get('offset', 0))
        limit  = int(request.GET.get('limit', 10))
        limit += offset
        drink_category = request.GET.get('drink_category', 'all')
        search_keyword = request.GET.get('search_keyword', None)


        try:
            if not drink_category == 'all':
                products = (Product.objects
                            .select_related('product_category', 'manufacture')
                            .filter(drinkdetail__drink_category__name = drink_category,
                                    name__icontains                   = search_keyword)
                            .prefetch_related('productimage_set', 'drinkdetail_set', 'drinkdetail_set__drink_category')
                            .order_by('-created_at')
                            )[offset:limit]

            else:
                products = (Product.objects
                            .select_related('product_category', 'manufacture')
                            .filter(name__icontains = search_keyword)
                            .prefetch_related('productimage_set',  'drinkdetail_set', 'drinkdetail_set__drink_category')
                            .order_by('-created_at')
                            )[offset:limit]


            drink_data = [{
                'id' : product.id,
                'product_image'   : [{
                    'id'          : product_image.id,
                    'image_url'   : product_image.image_url,
                }for product_image in product.productimage_set.all()],
                'product_category': product.product_category.name,
                'drink_category'  : product.drinkdetail_set.all()[0].drink_category.name if len(product.drinkdetail_set.all()) == 1 else "",
                'brewery'         : product.manufacture.name,
                'product_name'    : product.name,
                'price'           : product.price,
                'discount_rate'   : product.discount_rate,
                'create_at'       : product.created_at
            }for product in products]

            return JsonResponse({'MESSAGE': 'SUCCESS', "drink_data": drink_data}, status=200)

        except IntegrityError as e:
            return JsonResponse({"MESSAGE": "INTEGRITY_ERROR => " + e.args[0]}, status=400)
        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
        # except Exception as e:
        #     return JsonResponse({"MESSAGE": "ERROR => " + e.args[0]}, status=400)
