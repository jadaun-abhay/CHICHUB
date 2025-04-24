import json
from datetime import datetime

from django.conf import settings
from django.db.models import F
from django.http import JsonResponse

from apps.warehouse.enums import Status
from apps.warehouse.models import (
    Category,
    CategoryImages,
    Product,
    ProductImages,
)

from utils.functions import decode, encode, check_image_validity


# Create your views here.

def category_management(request, category_id= None):
    """Category Management by the ADMIN

    Args:
        request (HTTP Request Object): HTTP Request object
        category_id (int, optional): Primary Key for category selected. Defaults to None.

    Returns:
        HTTP Response: Depends upon the request method type
    """
    if request.method == "GET":
        if category_id:
            category_id = decode(category_id)
            queryset = Category.objects.filter(id= category_id).exclude(status= Status.DELETED).values('name', 'description', 'discount', pid= F('parent_id'))
            data = {'data': list(queryset)}
            return JsonResponse(data, status= 200)
        else:
            queryset = Category.objects.exclude(status= Status.DELETED).values( 'id', 'name', 'description', 'discount', pid= F('parent_id'))
            [category.update({'id': encode(category.get('id'))}) for category in queryset]
            data = {"data": list(queryset)}
            return JsonResponse(data, status= 200)
    elif request.method == "POST":
        data = request.POST
        name = data.get('name')
        description = data.get('description')
        parent_id = data.get('pid')
        discount = data.get('discount')
        images = request.FILES.getlist('categ_imgs') # To get a multidict
        if not name:
            response = {
                'error': True,
                'msg': 'Category name is required',
            }
            return JsonResponse(response, status=400)
        elif not description:
            response = {
                'error': True,
                'msg': 'Category description is required',
            }
            return JsonResponse(response, status=400)
        if parent_id and not parent_id.isnumeric():
            response = {
                'error': True,
                'msg': 'parent-id must be numeric',
            }
            return JsonResponse(response, status=400)
        if images:
            if not isinstance(images, list):
                response = {
                    'error': True,
                    'msg': 'images must be a list',
                }
                return JsonResponse(response, status=400)
            response = check_image_validity(images)
            if not isinstance(response, bool):
                return JsonResponse(response, status=400)
        if discount and not discount.isnumeric():
            response = {
                'error': True,
                'msg': 'discount must be numeric',
            }
            return JsonResponse(response, status=400)
        category, created = Category.objects.update_or_create(parent_id= parent_id, name= name, description= description, discount= discount, create_defaults= {'status': Status.CREATED})
        if images:
            instance_list = [CategoryImages(category= category, image= image, status= Status.CREATED) for image in images]
            CategoryImages.objects.bulk_create(instance_list)
        if not created:
            response = {
                'error': True,
                'msg': 'Category already exists',
            }
            return JsonResponse(response, status=400)
        response = {
            'error': False,
            'msg': 'Category created successfully',
        }
        return JsonResponse(response, status=201)
    elif request.method == 'PATCH':
        if not category_id:
            response = {
                'error':  True,
                'msg': 'Category id is required',
            }
            return JsonResponse(response, status=400)
        category_id = decode(category_id)
        queryset = Category.objects.filter(id= category_id).exclude(status= Status.DELETED)
        if not queryset:
            response = {
                'error': True,
                'msg': 'Category does not exist',
            }
            return JsonResponse(response, status=400)
        data = json.loads(request.body)
        name = data.get('name', queryset.first().name)
        description = data.get('description', queryset.first().description)
        discount = data.get('discount', queryset.first().discount)
        queryset.update(name= name, description= description, discount= discount, status = Status.UPDATED)
        response = {
            'error': False,
            'msg': 'Category updated successfully',
        }
        return JsonResponse(response, status=200)
    elif request.method == "DELETE":
        if not category_id:
            response = {
                'error': True,
                'msg': 'Category id is required',
            }
            return JsonResponse(response, status=400)
        category_id = decode(category_id)
        queryset = Category.objects.filter(id= category_id).exclude(status= Status.DELETED)
        if not queryset.exists():
            response = {
                'error': True,
                'msg': 'Category does not exists',
            }
            return JsonResponse(response, status=409)
        queryset.update(status = Status.DELETED)
        response = {
            'error': False,
            'msg': 'Category deleted successfully',
        }
        return JsonResponse(response, status=200)
    else:
        response = {
            'error': True,
            'msg': 'Method not allowed',
        }
        return JsonResponse(response, status=405)


def category_image_management(request, category_id= None, image_id= None):
    """Category Image Management by ADMIN

    Args:
        request (HTTP Request object): HTTP request object.
        category_id (int, optional): Primary key of the Category selected. Defaults to None.
        image_id (int, optional): Primary key of the image selected. Defaults to None.

    Returns:
        HTTP Response: Depending upon the request method type.
    """
    if request.method == 'GET':
        if not category_id:
            response = {
                'error': True,
                'msg': 'Category id is required',
            }
            return JsonResponse(response, status=400)
        category_id = decode(category_id)
        queryset = CategoryImages.objects.filter(category_id= category_id).exclude(status= Status.DELETED).values('id', 'image')
        [category_image.update({'id': encode(category_image.get('id'))}) for category_image in queryset]
        response = {
            'data': list(queryset),
        }
        return JsonResponse(response, status=200)
    elif request.method == 'POST':
        if not category_id:
            response = {
                'error': True,
                'msg': 'Category id is required',
            }
            return JsonResponse(response, status=400)
        category_id = decode(category_id)
        images = request.FILES.getlist('categ_imgs')
        if images:
            if not isinstance(images, list):
                response = {
                    'error': True,
                    'msg': 'Images must be a list',
                }
                return JsonResponse(response, status=400)
            response = check_image_validity(images)
            if not isinstance(response, bool):
                return JsonResponse(response, status=400)
        instance_list = [CategoryImages(category_id= category_id, image= image, status= Status.CREATED) for image in images]
        CategoryImages.objects.bulk_create(instance_list)
        response = {
            'error': False,
            'msg': 'Category images added successfully',
        }
        return JsonResponse(response, status=200)
    elif request.method == 'DELETE':
        if not category_id:
            response = {
                'msg': 'Category id is required',
            }
            return JsonResponse(response, status= 400)
        if not image_id:
            response = {
                'msg': 'Image id is required',
            }
            return JsonResponse(response, status=400)
        queryset = CategoryImages.objects.filter(id= decode(image_id)).exclude(status= Status.DELETED)
        if not queryset.exists():
            response = {
                'msg': 'Image does not exists',
            }
            return JsonResponse(response, status=409)
        queryset.update(status = Status.DELETED)
        response = {
            'msg': 'Image deleted successfully',
        }
        return JsonResponse(response, status=200)
    else:
        response = {
            'msg': 'Method not allowed',
        }
        return JsonResponse(response, status=405)


def product_management(request, category_id= None, product_id= None):
    """Product management by the ADMIN

    Args:
        request (HTTP Request object): HTTP Request object
        category_id (int, optional): Primary key for category selected. Defaults to None.
        product_id (int, optional): Primary key for product selected. Defaults to None.

    Returns:
        HTTP Response: Depends upon thr request method type.
    """
    
    if not category_id:
        response = {
            'msg': 'Category id is required',
        }
        return JsonResponse(response, status= 200)
    category_id = decode(category_id)
    queryset = Category.objects.filter(id= category_id).exclude(status= Status.DELETED)
    if not queryset:
        response = {
            'msg': 'Category does not exists',
        }
        return JsonResponse(response, status= 409)
    
    if request.method == 'GET':
        if product_id:
            product_id = decode(product_id)
            queryset = Product.objects.filter(category_id= category_id, id= product_id).exclude(status= Status.DELETED).values('id', 'name', 'description', 'category_id', 'price_per_unit', 'stocks_available', 'prod_status', 'discount')
            [product.update({'id': encode(product.get('id'))}) for product in queryset]
            response = {
                'data': list(queryset),
            }
            return JsonResponse(response, status= 200)
        queryset = Product.objects.filter(category_id= category_id).exclude(status= Status.DELETED).values('id', 'name', 'description', 'category_id', 'price_per_unit', 'stocks_available', 'prod_status', 'discount')
        [product.update({'id': encode(product.get('id')), 'category_id': encode(product.get('category_id'))}) for product in queryset]
        response = {
            'data': list(queryset),
        }
        return JsonResponse(response, status= 200)
    elif request.method == 'POST':
        data = request.POST
        name = data.get('name')
        description = data.get('description')
        price_per_unit = data.get('prod_price')
        stocks_available = data.get('stocks_qnty')
        prod_status = data.get('prod_status')
        discount = data.get('discount')
        images = request.FILES.getlist('prod_images')
        if not name:
            response = {
                'field': 'name',
                'msg': 'Product name is required',
            }
            return JsonResponse(response, status= 400)
        elif not description:
            response = {
                'field': 'description',
                'msg': 'Product description is required',
            }
            return JsonResponse(response, status= 400)
        elif not price_per_unit:
            response = {
                'field': 'prod_price',
                "msg": "Price of the product is not given",
            }
            return JsonResponse(response, status= 400)
        elif not stocks_available:
            response = {
                'field': 'no_of_stocks',
                'msg': 'No of stocks available in warehouse is required',
            }
            return JsonResponse(response, status= 400)
        elif not prod_status:
            response = {
                'field': 'prod_status',
                'msg': 'Status of the product is required',
            }
            return JsonResponse(response, data= 400)
        if discount and not discount.isnumeric:
            response = {
                "msg": "Discount must be numeric",
            }
            return JsonResponse(response, status= 400)
        if images:
            if not isinstance(images, list):
                response = {
                    'field': 'images',
                    'msg': 'Images must be given in the list',
                }
                return JsonResponse(response, status= 400)
            response = check_image_validity(images)
            if not isinstance(response, bool):
                return JsonResponse(response, status= 400)
        product, created = Product.objects.update_or_create(
            name= name, 
            description= description,
            category_id= category_id,
            price_per_unit= price_per_unit, 
            stocks_available= stocks_available, 
            prod_status= prod_status, 
            discount= discount,
            create_defaults= {'status': Status.CREATED},
        )
        if not created:
            response = {
                'msg': 'Product already exists',
            }
            return JsonResponse(response, status= 409)
        if images:
            instance_list = [ProductImages(product= product, image= image, status= Status.CREATED) for image in images]
            ProductImages.objects.bulk_create(instance_list)
        response = {
            'msg': 'Product has been added to the selected category',
        }
        return JsonResponse(response, status= 201)
    elif request.method == 'PATCH':
        if not product_id:
            response = {
                'msg': 'Product id is required',
            }
            return JsonResponse(response, status= 400)
        prod_queryset = Product.objects.filter(category_id= category_id, id= product_id).exclude(status= Status.DELETED)
        if not prod_queryset:
            response = {
                'msg': f'Product does not exists in {queryset.first().name} category',
            }
            return JsonResponse(response, status= 409)
        data = json.loads(request.body)
        name = data.get('name', prod_queryset.first().name)
        description = data.get('description', prod_queryset.first().description)
        price_per_unit = data.get('prod_price', prod_queryset.first().price_per_unit)
        stocks_available = data.get('stocks_qnty', prod_queryset.first().stocks_available)
        prod_status = data.get('prod_status', prod_queryset.first().prod_status)
        discount = data.get('discount', prod_queryset.first().discount)
        prod_queryset.update(status= Status.UPDATED, name= name, description= description, price_per_unit= price_per_unit, stocks_available= stocks_available, prod_status= prod_status)
        response = {
            'msg': 'Product has been updated successfully',
        }
        return JsonResponse(response, status= 200)
    elif request.method == 'DELETE':
        category_name = queryset.first().name
        if not product_id:
            response = {
                'msg': "Product id is required",
            }
            return JsonResponse(response, status= 409)
        product_id = decode(product_id)
        queryset = Product.objects.filter(id= product_id).exclude(status= Status.DELETED)
        if not queryset:
            response = {
                'msg': f'Product does not exists in {category_name} category',
            }
            return JsonResponse(response, status= 409)
        queryset.update(status= Status.DELETED, deleted_at= datetime.now())
        response = {
            'msg': 'Product has been deleted successfully',
        }
        return JsonResponse(response, status= 200)
    else:
        response = {
            'msg': 'Method not allowed',
        }
        return JsonResponse(response, status= 405)


def product_image_management(request, category_id= None, product_id= None):
    """Product image management by the ADMIN

    Args:
        request (HTTP request object): HTTP request object
        category_id (str, optional): Primary key for the selected category. Defaults to None.
        product_id (str, optional): Primary key for the selected product. Defaults to None.

    Returns:
        JSON response: Depending upon the request type.
    """
    
    if not category_id:
        response = {
            'msg': 'Category id is required',
        }
        return JsonResponse(response, status= 400)
    category_id = decode(category_id)
    categ_queryset = Category.objects.filter(id= category_id).exclude(status= Status.DELETED)
    if not categ_queryset:
        response = {
            'msg': 'Category does not exists',
        }
        return JsonResponse(response, status= 409)
    if not product_id:
        response = {
            'msg': 'Product id is required'
        }
        return JsonResponse(response, status= 400)
    product_id= decode(product_id)
    prod_queryset = Product.objects.filter(id= product_id).exclude(status= Status.DELETED)
    if not prod_queryset:
        response = {
            'msg': f'Product does not exists in {categ_queryset.first().name} category',
        }
        return JsonResponse(response, status= 409)
    
    if request.method == 'GET':
        prod_queryset = ProductImages.objects.filter(product__category_id= category_id).exclude(product__status= Status.DELETED).exclude(status= Status.DELETED).values('id', 'product_id', 'image')
        [prod_image.update({"id": encode(prod_image.get("id")), "product_id": encode(prod_image.get("product_id")),}) for prod_image in prod_queryset]
        response = {
            'data': list(prod_queryset),
        }
        return JsonResponse(response, status= 200)
    elif request.method == 'POST':
        if not product_id:
            response = {
                'msg': 'Product id is required',
            }
            return JsonResponse(response, status= 400)
        product_id = decode(product_id)
        images = request.FILES.getlist('prod_images')
        if images:
            if not isinstance(images, list):
                response = {
                    'msg': 'Images must be a list',
                }
                return JsonResponse(response, status= 400)
            response = check_image_validity(images)
            if not isinstance(response, bool):
                return JsonResponse(response, status= 400)
        instance_list = [ProductImages(image= image, product_id= product_id, status= Status.DELETED) for image in images]
        ProductImages.objects.bulk_create(instance_list)
        response = {
            'msg': 'Product images added successfully',
        }
        return JsonResponse(response, status= 201)
    elif request.method == 'DELETE':
        data = json.loads(request.body)
        prod_images = data.get('prod_imgs')
        prod_images = [decode(image_id) for image_id in prod_images]
        instance_list = [ProductImages(id= image_id) for image_id in prod_images]
        for instance in instance_list:
            instance.status = Status.DELETED
            instance.deleted_at = datetime.now()
        ProductImages.objects.bulk_update(instance_list, ['status', 'deleted_at'])
        response = {
            'msg': 'Product images are deleted successfully',
        }
        return JsonResponse(response, status= 400)
    else:
        response = {
            'msg': 'Method not allowed',
        }
        return JsonResponse(response, status= 405)
