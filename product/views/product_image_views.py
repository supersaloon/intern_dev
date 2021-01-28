import uuid
import json

from django.http  import JsonResponse
from django.views import View
from django.db    import transaction

from user.models    import Administrator
from product.models import ProductImage, Product
from product.utils  import s3_client


class ProductImageView(View):
    # @signin_decorator
    @transaction.atomic
    def post(self, request):
        try:
            data = request.POST
            print(f"data: {data}")
            product_id = data['product_id']

            if not Product.objects.filter(id=product_id):
                return JsonResponse({"MESSAGE": "PRODUCT NOT EXIST"}, status=400)

            product_images = request.FILES.getlist('product_image')
            for product_image in product_images:
                filename = str(uuid.uuid1()).replace('-', '')
                response = s3_client.upload_fileobj(
                    product_image,
                    "rip-dev-bucket",
                    f'intern_dev/{filename}',
                    ExtraArgs={
                        "ContentType": product_image.content_type
                    }
                )
                image_url = f"https://s3.ap-northeast-2.amazonaws.com/rip-dev-bucket/intern_dev/{filename}"

                ProductImage.objects.create(
                    product_id = product_id,
                    image_url  = image_url,
                )

            return JsonResponse({'MESSAGE': 'SUCCESS'}, status=201)

        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
        except Exception as e:
            return JsonResponse({"MESSAGE": "Exception => " + e.args[0]}, status=400)


    #@signin_decorator
    def delete(self, request, product_image_id):
        try:
            if not ProductImage.objects.filter(id=product_image_id):
                return JsonResponse({"MESSAGE": "PRODUCT NOT EXIST"}, status=400)

            product_image = ProductImage.objects.get(id=product_image_id)
            filename = product_image.image_url.split('/rip-dev-bucket/')[1]
            response = s3_client.delete_object(
                Bucket = "rip-dev-bucket",
                Key    = filename,
            )

            product_image.delete()

            return JsonResponse({'MESSAGE': 'SUCCESS'}, status=200)

        except Exception as e:
            return JsonResponse({"MESSAGE": "Exception => " + e.args[0]}, status=400)
