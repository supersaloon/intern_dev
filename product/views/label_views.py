import uuid

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
            # label_ids = []
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
                label_image_url = f"https://s3.ap-northeast-2.amazonaws.com/rip-dev-bucket/intern_dev/{filename}"

                # label = Label.objects.create(
                #     product_id = product_id,
                #     image_url  = image_url,
                # )
                # label_ids.append(label.id)

            return JsonResponse({'MESSAGE': 'SUCCESS', 'label': label_image_url}, status=201)

        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
        except Exception as e:
            return JsonResponse({"MESSAGE": "Exception => " + e.args[0]}, status=400)
