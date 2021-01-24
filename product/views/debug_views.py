import boto3
import uuid
import json

from django.http  import JsonResponse
from django.views import View
from django.db    import transaction
from django.db.utils import IntegrityError

from user.models    import Administrator
from product.models import ProductCategory, DrinkCategory, IndustrialProductInfo, Manufacture, ManufactureType, Volume, \
                           Label, TasteMatrix, DrinkDetail, DrinkDetailVolume, Product, Tag, ProductImage, Paring, BaseMaterial
from my_settings  import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY



class DrinkView(View):
    # @signin_decorator
    @transaction.atomic
    def post(self, request):
        try:
            # data = json.loads(request.body)
            data = request.POST
            # data: <QueryDict: {'product_name': ['박채훈의 입벌구주'], 'subtitle': ['입만 벌리면']}>
            print(f'data: {data}')
            print()
            print()
            product_name = data.get('product_name')  # 키 값이 없으면 None 반환
            print(f"data.get('product_name'): {product_name}")
            # data.get('product_name'): 박채훈의 입벌구주

            product_name = data['product_name']  # 키 값이 없으면 KeyError 반환
            print(f"data['product_name']: {product_name}")
            # data['product_name']: 박채훈의 입벌구주

            product_images = request.FILES.get('product_image')  # 키 값이 없으면 None 반환
            print(f"request.FILES.get('product_images'): {product_images}")
            # request.FILES.get('images'): sing_ha.jpg

            product_images = request.FILES.getlist('product_image')  # 키 값이 없으면 빈 리스트 반환
            print(f"request.FILES.getlist('product_images'): {product_images}")
            # request.FILES.getlist('images'): [<InMemoryUploadedFile: error_500.png (image/png)>, <InMemoryUploadedFile: sing_ha.jpg (image/jpeg)>]

            for image in product_images:
                print(f"image: {image}")
                # image: error_500.png
                # image: sing_ha.jpg

            product_image = request.FILES['product_image']  # 키 값이 없으면 KeyError 반환
            print(f"request.FILES['product_image']: {product_image}")
            # request.FILES['images']: sing_ha.jpg


            paring = data.getlist('paring')
            print(f"data.getlist('paring'): {paring}")
            # data.getlist('paring'): ['삼겹살', '가브리살', '살치살']


            # parings 라는 key 값 하나에 json 으로 전부 태워서 전송
            # parings = json.loads(data.get('parings'))
            # print(f"data.getlist('parings'): {parings}")
            # for i in parings:
            #     print(i)


            volume = data.getlist('volume')
            print(f"volume: {volume}")
            # volume = json.loads(data.getlist('volume'))
            # print(f"json.loads(data.getlist('volume')): {volume}")
            for i in volume:
                print(json.loads(i)['volume'])
                print(json.loads(i)['price'])


            # debug input data


            drink_data = "hi"

            return JsonResponse({'MESSAGE': 'SUCCESS', "drink_data": drink_data}, status=201)
        except IntegrityError as e:
            return JsonResponse({"MESSAGE": "INTEGRITY_ERROR => " + e.args[0]}, status=400)
        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
