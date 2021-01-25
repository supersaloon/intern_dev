from django.http  import JsonResponse
from django.views import View
from django.db    import transaction

from product.models import ProductCategory, DrinkCategory


class CategoryListView(View):
    # @signin_decorator
    @transaction.atomic
    def get(self, request):

        try:
            category_list_data = {
                'product_category': [{
                    'id'              : product_category.id,
                    'product_category': product_category.name,
                }for product_category in ProductCategory.objects.all()],
                'drink_category': [{
                    'id'            : drink_category.id,
                    'drink_category': drink_category.name,
                } for drink_category in DrinkCategory.objects.all()],
            }

            return JsonResponse({'MESSAGE': 'SUCCESS', "category_list_data": category_list_data}, status=200)

        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
