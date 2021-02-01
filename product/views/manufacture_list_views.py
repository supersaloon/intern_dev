import json

from django.http     import JsonResponse
from django.views    import View
from django.db       import transaction
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404

from user.models    import Administrator
from product.models import Manufacture, ManufactureType


class ManufactureListView(View):
    # @signin_decorator
    def get(self, request):
        try:
            data = json.loads(request.body)

            manufactures = Manufacture.objects.filter(manufacture_type__name=data['manufacture_type'])

            manufacture_data = [{
                'id'                         : manufacture.id,
                'name'                       : manufacture.name,
            }for manufacture in manufactures]

            return JsonResponse({'MESSAGE': 'SUCCESS', 'manufacture_data': manufacture_data}, status=200)

        except Manufacture.DoesNotExist as e:
                return JsonResponse({"MESSAGE": "MANUFACTURE NOT EXIST"}, status=400)
        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
