from django.db import models

# Create your models here.
# 此时的是明文存储,所以比较不安全,这种方法不可行
# class User(models.Model):
#     username = models.CharField(max_length=20)
#     password = models.CharField(max_length=20)
#     mobile = models.CharField(max_length=20)