from django.db import models

from apps.warehouse.enums import Status, ProductStatus


# Create your models here.

class BaseModel(models.Model):
    status = models.IntegerField(default= Status.CREATED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True)

    class Meta:
        abstract = True


class Category(BaseModel):
    name = models.CharField(max_length= 50)
    description = models.TextField()
    parent = models.ForeignKey('self', on_delete= models.SET_NULL, null= True, related_name= 'children')
    discount = models.FloatField(null= True)

from apps.warehouse.functions import categ_path_generator

class CategoryImages(BaseModel):
    def categ_img_path(self, filename):
        generated_path = '/'.join(categ_path_generator(self.category.id).split('/')[:-2])
        path = 'categories/' + generated_path + '/' + filename
        return path
    category = models.ForeignKey(Category, on_delete= models.SET_NULL, null= True, related_name= 'images')
    image = models.ImageField(upload_to= categ_img_path)


class Product(BaseModel):
    name = models.CharField(max_length= 50)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete= models.SET_NULL, null= True, related_name= 'products')
    price_per_unit = models.FloatField()
    stocks_available = models.IntegerField()
    prod_status = models.IntegerField(default= ProductStatus.ACTIVE)
    discount = models.FloatField(null= True)


class ProductImages(BaseModel):
    def prod_img_path(self, filename):
        pass
    product = models.ForeignKey(Product, on_delete= models.CASCADE, null= True, related_name= 'images')
    image = models.ImageField(upload_to= prod_img_path)
