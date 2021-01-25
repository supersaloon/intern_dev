import uuid
import json

from django.http  import JsonResponse
from django.views import View
from django.db    import transaction
from django.db.utils import IntegrityError

from user.models    import Administrator
from product.models import ProductCategory, DrinkCategory, IndustrialProductInfo, Manufacture, ManufactureType, Volume, \
                           Label, TasteMatrix, DrinkDetail, DrinkDetailVolume, Product, Tag, ProductImage, Paring, BaseMaterial
from product.utils import s3_client


class ManufactureView(View):
    # @signin_decorator
    @transaction.atomic
    def post(self, request):
        try:
            # data = request.POST
            data = json.loads(request.body)

            # manufacture_types 테이블
            manufacture_type, flag = ManufactureType.objects.get_or_create(name=data['manufacture_type'])

            # manufactures 테이블
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

            return JsonResponse({'MESSAGE': 'SUCCESS'}, status=201)

        except IntegrityError as e:
            return JsonResponse({"MESSAGE": "INTEGRITY_ERROR => " + e.args[0]}, status=400)
        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)


    # @signin_decorator
    @transaction.atomic
    def get(self, request, manufacture_id):
        try:
            # manufacture_types 테이블
            manufacture = Manufacture.objects.select_related('manufacture_type').get(id=manufacture_id)

            manufacture_data = {
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

        except Manufacture.DoesNotExist as e:
                return JsonResponse({"MESSAGE": e}, status=200)
        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)



    @transaction.atomic
    def patch(self, request, manufacture_id):
        try:
            # print(json.loads(request.body))
            print(f'request.POST: {request.POST}')
            print(f'request.GET: {request.GET}')
            # print(f'request.FILES: {request.FILES}')
            # print(f'request.META: {request.META}')
            # print(f'request.COOKIES: {request.COOKIES}')
            # print(manufacture_id)

            # print(request.)


            # # manufacture_types 테이블
            # manufacture_type, flag = ManufactureType.objects.get_or_create(name=data['manufacture_type'])
            #
            # # manufactures 테이블
            # manufacture = Manufacture.objects.get(id=manufacture_id)
            #
            # manufacture(
            #     manufacture_type            = manufacture_type,
            #     name                        = data['manufacture_name'],
            #     origin                      = data['origin'],
            #     representative_name         = data['representative_name'],
            #     email                       = data['email'],
            #     phone_number                = data['phone_number'],
            #     address                     = data['address'],
            #     company_registration_number = data['company_registration_number'],
            #     mail_order_report_number    = data['mail_order_report_number'],
            # ).save()


            return JsonResponse({'MESSAGE': 'SUCCESS'}, status=200)

        except Manufacture.DoesNotExist as e:
            return JsonResponse({"MESSAGE": e.args[0]}, status=200)
        except IntegrityError as e:
            return JsonResponse({"MESSAGE": "INTEGRITY_ERROR => " + e.args[0]}, status=400)
        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)


    #@signin_decorator
    def delete(self, request, manufacture_id):
        try:
            manufacture = Manufacture.objects.get(id=manufacture_id)
            manufacture.delete()

            return JsonResponse({'MESSAGE': 'SUCCESS'}, status=200)

        except Manufacture.DoesNotExist as e:
            return JsonResponse({"MESSAGE": e.args[0]}, status=200)
        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
