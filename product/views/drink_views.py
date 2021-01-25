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
from product.utils import s3_client


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


            # manufacture_types 테이블
            manufacture_type, flag = ManufactureType.objects.get_or_create(name=data['manufacture_type'])


            # manufactures 테이블
            manufacture, flag = Manufacture.objects.get_or_create(
                name                        = data['manufacture_name'],
                manufacture_type            = manufacture_type,
                origin                      = data['origin'],
                representative_name         = data['representative_name'],
                email                       = data['email'],
                phone_number                = data['phone_number'],
                address                     = data['address'],
                company_registration_number = data['company_registration_number'],
                mail_order_report_number    = data['mail_order_report_number'],
            )


            # product_category 테이블
            product_category, flag = ProductCategory.objects.get_or_create(name=data['product_category'])


            # products 테이블
            product = Product.objects.create(
                name             = data['product_name'],
                subtitle         = data['subtitle'],
                price            = data['price'],
                content          = data['content'],
                is_damhwa_box    = data['is_damhwa_box'],
                discount_rate    = data['discount_rate'],
                award            = data['award'],
                product_category = product_category,
                manufacture      = manufacture,
                uploader         = Administrator.objects.get(name   = "homer"),
            )

            # products 테이블에 태그 추가
            tags = data.getlist('tag')
            for tag in tags:
                tag, flag = Tag.objects.get_or_create(name=tag)
                product.product_tag.add(tag)
                print(f"태그: {tag.name} 추가 완료")


            # product_images 테이블  # KEY: product_image
            if request.FILES.getlist('product_image'):
                product_images = request.FILES.getlist('product_image')

                for product_image in product_images:
                    filename = str(uuid.uuid1()).replace('-', '')
                    s3_client.upload_fileobj(
                        product_image,
                        "rip-dev-bucket",
                        f'intern_dev/{filename}',
                        ExtraArgs={
                            "ContentType": product_image.content_type
                        }
                    )
                    image_url = f"https://s3.ap-northeast-2.amazonaws.com/rip-dev-bucket/intern_dev/{filename}"

                    ProductImage.objects.create(
                        product   = product,
                        image_url = image_url,
                    )


            # labels 테이블  # KEY: label
            labels = request.FILES.getlist('label') if request.FILES.getlist('label') else None
            if labels:
                for label in labels:
                    filename = str(uuid.uuid1()).replace('-', '')
                    s3_client.upload_fileobj(
                        label,
                        "rip-dev-bucket",
                        f'intern_dev/{filename}',
                        ExtraArgs={
                            "ContentType": product_image.content_type
                        }
                    )
                    image_url = f"https://s3.ap-northeast-2.amazonaws.com/rip-dev-bucket/intern_dev/{filename}"
                    Label.objects.create(
                        product   = product,
                        label_url = image_url,
                    )


            # industrial_product_infos 테이블
            IndustrialProductInfo.objects.create(
                product                        = product,
                food_type                      = data['food_type'],
                business_name                  = data['business_name'],
                location                       = data['location'],
                shelf_life                     = data['shelf_life'],
                volume_by_packing              = data['volume_by_packing'],
                base_material_name_and_content = data['base_material_name_and_content'],
                nutrient                       = data['nutrient'],
                gmo                            = data['gmo'],
                import_declaration             = data['import_declaration'],
            )


            # drink_category 테이블
            drink_category, flag = DrinkCategory.objects.get_or_create(name=data['drink_category'])


            # drink_details 테이블
            drink_detail =DrinkDetail.objects.create(
                product                 = product,
                drink_category          = drink_category,
                alcohol_content         = data['alcohol_content'],
                fragrance               = data['fragrance'],
                flavor                  = data['flavor'],
                finish                  = data['finish'],
                with_who                = data['with_who'],
                what_situation          = data['what_situation'],
                what_mood               = data['what_mood'],
                what_profit             = data['what_profit'],
                recommend_situation     = data['recommend_situation'],
                recommend_eating_method = data['recommend_eating_method'],
                additional_info         = data['additional_info'],
            )


            # taste_matrixs 테이블
            TasteMatrix.objects.create(
                drink_detail = drink_detail,
                body         = data['body'] if data.get('body') else 0,
                acidity      = data['acidity'] if data.get('acidity') else 0,
                sweetness    = data['sweetness'] if data.get('sweetness') else 0,
                tannin       = data['tannin'] if data.get('tannin') else 0,
                bitter       = data['bitter'] if data.get('bitter') else 0,
                sparkling    = data['sparkling'] if data.get('sparkling') else 0,
                light        = data['light'] if data.get('light') else 0,
                turbidity    = data['turbidity'] if data.get('turbidity') else 0,
                savory       = data['savory'] if data.get('savory') else 0,
                gorgeous     = data['gorgeous'] if data.get('gorgeous') else 0,
                spicy        = data['spicy'] if data.get('spicy') else 0,
            )


            # parings 테이블
            parings = data.getlist('paring')
            for paring in parings:
                paring = json.loads(paring)
                paring, flag = Paring.objects.get_or_create(
                    name        = paring['name'],
                    description = paring['description'],
                )
                drink_detail.drink_detail_paring.add(paring)
                print(f"페어링: {paring.name}, 설명: {paring.description} 추가 완료")


            # base_materials 테이블
            base_materials = data.getlist('base_material')
            for base_material in base_materials:
                base_material, flag = BaseMaterial.objects.get_or_create(
                    name = base_material
                )
                drink_detail.drink_detail_base_material.add(base_material)
                print(f"원재료: {base_material.name} 추가 완료")


            # DrinkDetailVolume 테이블
            volume_and_prices = data.getlist('volume_and_price')
            for volume_and_price in volume_and_prices:
                volume_and_price = json.loads(volume_and_price)  # {"volume": "500ml", "price": "500"}

                price = volume_and_price['price']
                volume, flag = Volume.objects.get_or_create(name=volume_and_price['volume'])

                DrinkDetailVolume.objects.get_or_create(
                    drink_detail = drink_detail,
                    volume       = volume,
                    price        = price,
                )


            # 모든 데이터 입력 후 마지막에 is_done 을 True로 수정 -> 추후 임시저장 모드를 지원하기 위함
            product.is_done = True
            product.save()

            return JsonResponse({'MESSAGE': 'SUCCESS'}, status=201)

        except IntegrityError as e:
            return JsonResponse({"MESSAGE": "INTEGRITY_ERROR => " + e.args[0]}, status=400)
        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)


    #@signin_decorator
    def delete(self, request, product_id):
        try:
            product_images = ProductImage.objects.filter(product_id=product_id)
            for product_image in product_images:
                filename = product_image.image_url.split('/rip-dev-bucket/')[1]
                response = s3_client.delete_object(
                    Bucket="rip-dev-bucket",
                    Key=filename,
                )
                print(f"response: {response}")

            product = Product.objects.get(id=product_id)
            product.delete()




            return JsonResponse({'MESSAGE': 'SUCCESS'}, status=200)

        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
        except Exception as e:
            return JsonResponse({"MESSAGE": "Exception => " + e.args[0]}, status=400)





    @transaction.atomic
    def get(self, request, product_id):
        try:

            product = Product.objects.get(product_id=product_id)


            # drink_data = {
            #     product_category =
            #     manufacture_type
            #     manufacture_name
            #     origin
            #     representative_name
            #     email
            #     phone_number
            #     address
            #     company_registration_number
            #     mail_order_report_number
            #
            #     product_name
            #     subtitle
            #     price
            #     content
            #     is_damhwa_box
            #     discount_rate
            #     award
            #
            #     tag
            #
            #     product_image
            #
            #     label
            #
            #     food_type
            #     business_name
            #     location
            #     shelf_life
            #     volume_by_packing
            #     base_material_name_and_content
            #     nutrient
            #     gmo
            #     import_declaration
            #
            #     drink_category
            #
            #     alcohol_content
            #     fragrance  # 향
            #     flavor  # 맛
            #     finish  # 피니시
            #     with_who  # 누구와?
            #     what_situation  # 어느 상황에?
            #     what_mood  # 어떤 기분에?
            #     what_profit  # 좋은 점은?
            #     recommend_situation  # 맛+어울리는 상황
            #     recommend_eating_method  # 추천 안주 및 음용방법
            #     additional_info  # 기타정보
            #
            #     body  # 바디감
            #     acidity  # 산미
            #     sweetness  # 단맛
            #     tannin  # 타닌
            #     bitter  # 쓴맛
            #     sparkling  # 탄산감
            #     light  # 담백
            #     turbidity  # 탁도
            #     savory  # 풍미
            #     gorgeous  # 화려
            #     spicy  # 매운맛
            #
            #     paring
            #
            #     base_material
            #
            #     volume_and_price
            #
            # }



            return JsonResponse({'MESSAGE': 'SUCCESS'}, status=201)

        except IntegrityError as e:
            return JsonResponse({"MESSAGE": "INTEGRITY_ERROR => " + e.args[0]}, status=400)
        except KeyError as e:
            return JsonResponse({"MESSAGE": "KEY_ERROR => " + e.args[0]}, status=400)
