import boto3
import uuid
import json

from django.http  import JsonResponse
from django.views import View
from django.db    import transaction
from django.shortcuts import get_object_or_404
from django.http import Http404

from user.models    import Administrator
from product.models import Label, Product
from product.utils  import s3_client


class LabelView(View):
    # @signin_decorator
    @transaction.atomic
    def post(self, request):
        try:
            data = request.POST
            product_id = data.get('product_id') if data.get('product_id') else None

            if product_id:
                if not Product.objects.filter(id=product_id):
                    return JsonResponse({"MESSAGE": "PRODUCT NOT EXIST"}, status=400)

            labels = request.FILES.getlist('label')
            label_ids = []
            for label in labels:
                filename = str(uuid.uuid1()).replace('-', '')
                response = s3_client.upload_fileobj(
                    label,
                    "rip-dev-bucket",
                    f'intern_dev/{filename}',
                    ExtraArgs={
                        "ContentType": label.content_type
                    }
                )
                image_url = f"https://s3.ap-northeast-2.amazonaws.com/rip-dev-bucket/intern_dev/{filename}"

                label = Label.objects.create(
                    product_id = product_id,
                    image_url  = image_url,
                )
                label_ids.append(label.id)

            return JsonResponse({'MESSAGE': 'SUCCESS', 'label_ids': label_ids}, status=201)

        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
        except Exception as e:
            return JsonResponse({"MESSAGE": "Exception => " + e.args[0]}, status=400)


    #@signin_decorator
    def delete(self, request, label_id):
        try:
            label = get_object_or_404(Label, id=label_id)
            filename = label.image_url.split('/rip-dev-bucket/')[1]
            response = s3_client.delete_object(
                Bucket = "rip-dev-bucket",
                Key    = filename,
            )

            label.delete()

            return JsonResponse({'MESSAGE': 'SUCCESS'}, status=200)

        except Http404 as e:
            return JsonResponse({"MESSAGE": "LABEL NOT EXIST"}, status=400)
        except Exception as e:
            return JsonResponse({"MESSAGE": "Exception => " + e.args[0]}, status=400)
