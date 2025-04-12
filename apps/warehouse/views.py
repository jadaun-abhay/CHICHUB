import json

from django.conf import settings
from django.db.models import F
from django.http import JsonResponse

from apps.warehouse.enums import Status
from apps.warehouse.functions import check_image_validity
from apps.warehouse.models import (
    Category,
    CategoryImages,
)

from utils.functions import decode, encode


# Create your views here.

def category_management(request, category_id= None):
    """
    Category management by ADMIN
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
        response = {'data': list(queryset)}
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

