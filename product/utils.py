import boto3
import uuid

from django.http      import JsonResponse

from product.models import ProductImage, Product
from my_settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY


s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)


def reverse_foreign_key_finder(Model):
    for related_object in Model._meta.related_objects:
        print(
            related_object.related_model.__name__,
            related_object.remote_field.name,
            related_object.get_accessor_name(),
            sep='\t',
        )




# image_url = f"https://///{filename}"
# input
# 이미지 파일 들어있는 리스트  - image_files
# 버킷 URL                   - bucket_url   : s3.ap-northeast-2.amazonaws.com
# 버킷 이름                  - bucket_name    : rip-dev-bucket
# 버킷 내 경로               - bucket_directory: intern_dev
# output
# 이미지 URL 들어있는 리스트   - image_urls
def s3_image_uploader(image_files, bucket_url, bucket_name, bucket_directory):
    image_urls = []
    for image_file in image_files:
        print("=======================================================")
        print(f"image_files: {image_files}")
        print(f"image_file: {image_file}")
        filename = str(uuid.uuid1()).replace('-', '')
        response = s3_client.upload_fileobj(
            image_file,
            f"{bucket_name}",
            f"{bucket_directory}/{filename}",
            ExtraArgs={
                "ContentType": image_file.content_type
            }
        )
        print(f'boto3 response: {response}')
        # image_url = f"https://s3.ap-northeast-2.amazonaws.com/rip-dev-bucket/intern_dev/{filename}"
        image_url = f"https://{bucket_url}/{bucket_name}/{bucket_directory}/{filename}"
        print(f"image_url: {image_url}")
        image_urls.append(image_url)
        print(f"image_urls: {image_urls}")
    return image_urls



# def s3_image_destroyer(self, request, product_image_id):
#     try:
#         product_image = get_object_or_404(ProductImage, id=product_image_id)
#         filename = product_image.image_url.split('/rip-dev-bucket/')[1]
#         response = s3_client.delete_object(
#             Bucket = "rip-dev-bucket",
#             Key    = filename,
#         )
#
#         product_image.delete()
#
#         return JsonResponse({'MESSAGE': 'SUCCESS'}, status=200)
