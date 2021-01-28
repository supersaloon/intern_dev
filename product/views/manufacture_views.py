import json

from django.http     import JsonResponse
from django.views    import View
from django.db       import transaction
from django.db.utils import IntegrityError
from django.shortcuts import get_object_or_404
from django.http import Http404

from user.models    import Administrator
from product.models import Manufacture, ManufactureType


class ManufactureView(View):
    # @signin_decorator
    @transaction.atomic
    def post(self, request):
        try:
            data = json.loads(request.body)

            manufacture_type, flag = ManufactureType.objects.get_or_create(name=data['manufacture_type'])

            manufacture, flag= Manufacture.objects.get_or_create(
                manufacture_type            = manufacture_type,
                name                        = data['manufacture_name'],
                origin                      = data['origin'],
                representative_name         = data['representative_name'],
                email                       = data['email'],
                phone_number                = data['phone_number'],
                address                     = data['address'],
                company_registration_number = data['company_registration_number'],
                mail_order_report_number    = data['mail_order_report_number'],
            )

            # Fasle -> 기존 값을 가져옴(create하지 아니함)
            if not flag:
                return JsonResponse({'MESSAGE': 'MANUFACTURE ALREADY EXIST'}, status=202)

            return JsonResponse({'MESSAGE': 'SUCCESS', 'manufacture_id': manufacture.id}, status=201)

        except IntegrityError as e:
            return JsonResponse({"MESSAGE": "INTEGRITY_ERROR => " + e.args[0]}, status=400)
        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)


    # @signin_decorator
    @transaction.atomic
    def get(self, request, manufacture_id):
        try:
            manufacture = get_object_or_404(Manufacture, id=manufacture_id)

            manufacture_data = {
                'id'                         : manufacture.id,
                'manufacture_type'           : manufacture.manufacture_type.name,
                'name'                       : manufacture.name,
                'origin'                     : manufacture.origin,
                'representative_name'        : manufacture.representative_name,
                'email'                      : manufacture.email,
                'phone_number'               : manufacture.phone_number,
                'address'                    : manufacture.address,
                'company_registration_number': manufacture.company_registration_number,
                'mail_order_report_number'   : manufacture.mail_order_report_number,
            }

            return JsonResponse({'MESSAGE': 'SUCCESS', 'manufacture_data': manufacture_data}, status=200)

        except Http404 as e:
                return JsonResponse({"MESSAGE": "MANUFACTURE NOT EXIST"}, status=400)
        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)



    @transaction.atomic
    def patch(self, request, manufacture_id):
        try:
            data = json.loads(request.body)

            manufacture = get_object_or_404(Manufacture, id=manufacture_id)

            manufacture_type, flag = ManufactureType.objects.get_or_create(name=data['manufacture_type'])

            manufacture.manufacture_type            = manufacture_type
            manufacture.name                        = data['manufacture_name']
            manufacture.origin                      = data['origin']
            manufacture.representative_name         = data['representative_name']
            manufacture.email                       = data['email']
            manufacture.phone_number                = data['phone_number']
            manufacture.address                     = data['address']
            manufacture.company_registration_number = data['company_registration_number']
            manufacture.mail_order_report_number    = data['mail_order_report_number']

            manufacture.save()

            return JsonResponse({'MESSAGE': 'SUCCESS'}, status=200)

        except Http404 as e:
                return JsonResponse({"MESSAGE": "MANUFACTURE NOT EXIST"}, status=400)
        except IntegrityError as e:
            return JsonResponse({"MESSAGE": "INTEGRITY_ERROR => " + e.args[0]}, status=400)
        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)


    #@signin_decorator
    def delete(self, request, manufacture_id):
        try:
            manufacture = get_object_or_404(Manufacture, id=manufacture_id)
            manufacture.delete()

            return JsonResponse({'MESSAGE': 'SUCCESS'}, status=200)

        except Http404 as e:
                return JsonResponse({"MESSAGE": "MANUFACTURE NOT EXIST"}, status=400)
        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
