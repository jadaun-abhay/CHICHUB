from django.db import models

# Create your models here.

class Status(models.IntegerChoices):
    CREATED = 1
    UPDATED = 2
    DELETED = 3

class BaseModel(models.Model):
    status = models.IntegerField(choices= Status, default= Status.CREATED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class Category(BaseModel):
    name = models.CharField(max_length= 50)
    description = models.TextField()
    parent = models.ForeignKey('self', on_delete= models.SET_NULL, null= True, related_name= 'children')
    discount = models.FloatField(null= True)


class CategoryImages(BaseModel):
    category = models.ForeignKey(Category, on_delete= models.SET_NULL, null= True, related_name= 'images')
    image = models.ImageField()


class ProductStatus(models.IntegerChoices):
    ACTIVE = 1
    INACTIVE = 2

class Product(BaseModel):
    name = models.CharField(max_length= 50)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete= models.SET_NULL, null= True, related_name= 'products')
    price_per_unit = models.FloatField()
    stocks_available = models.IntegerField()
    status = models.IntegerField(choices= ProductStatus)
    discount = models.FloatField(null= True)


class ProductImages(BaseModel):
    product = models.ForeignKey(Product, on_delete= models.CASCADE, null= True, related_name= 'images')
    image = models.ImageField()
