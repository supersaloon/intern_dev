import boto3

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
