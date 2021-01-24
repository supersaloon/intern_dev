from django.db import models


class AdministratorType(models.Model):
    name = models.CharField(max_length=20)

    class Meta:
        db_table = 'administrator_types'


class Administrator(models.Model):
    administrator_type = models.ForeignKey(AdministratorType, on_delete=models.PROTECT)
    name               = models.CharField(max_length=20)
    account            = models.CharField(max_length=20)
    password           = models.CharField(max_length=2000)
    created_at         = models.DateTimeField(auto_now_add = True)
    updated_at         = models.DateTimeField(auto_now = True)

    class Meta:
        db_table = 'administrators'
