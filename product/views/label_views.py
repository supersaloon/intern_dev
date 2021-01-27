import boto3
import uuid
import json

from django.http  import JsonResponse
from django.views import View
from django.db    import transaction

from user.models    import Administrator
from product.models import Label
from product.utils  import s3_client


class LabelView(View):
    # @signin_decorator
    @transaction.atomic
    def post(self, request):
        try:
            data = json.loads(request.body)
            product_id = data['product_id']

            labels = request.FILES.getlist('label')
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

                Label.objects.create(
                    product_id = product_id,
                    image_url  = image_url,
                )

            return JsonResponse({'MESSAGE': 'SUCCESS'}, status=201)

        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
        except Exception as e:
            return JsonResponse({"MESSAGE": "Exception => " + e.args[0]}, status=400)


    #@signin_decorator
    def delete(self, request, label_id):
        try:
            label = Label.objects.get(id=label_id)
            filename = label.image_url.split('/rip-dev-bucket/')[1]
            response = s3_client.delete_object(
                Bucket = "rip-dev-bucket",
                Key    = filename,
            )

            label.delete()

            return JsonResponse({'MESSAGE': 'SUCCESS'}, status=200)

        except Exception as e:
            return JsonResponse({"MESSAGE": "Exception => " + e.args[0]}, status=400)
