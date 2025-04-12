import json

from django.conf import settings
from django.db.models import F
from django.http import JsonResponse

from apps.warehouse.enums import Status
from apps.warehouse.models import (
    Category,
    CategoryImages,
)

from utils.functions import decode


# Create your views here.

def category_management(request, category_id= None):
    """
    Category management by ADMIN
    """
    if request.method == "GET":
        if category_id:
            category_id = decode(category_id)
            queryset = Category.objects.filter(id= category_id).exclude(status= Status.DELETED).values('id', 'name', 'description', 'discount', pid= F('parent_id'))
            data = {'data': list(queryset)}
            return JsonResponse(data, status= 200)
        else:
            queryset = Category.objects.exclude(status= Status.DELETED).values('id', 'name', 'description', 'discount', pid= F('parent_id'))
            data = {"data": list(queryset)}
            return JsonResponse(data, status= 200)
    elif request.method == "POST":
        data = request.POST
        name = data.get('name')
        description = data.get('description')
        parent_id = data.get('pid')
        discount = data.get('discount')
        images = request.FILES.getlist('categ_imgs') # To get a multidict

        print(images)
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
            for image in images:
                img_extension = image.name.split('.')[-1]
                img_content_type = image.content_type
                if img_extension not in settings.WHITELISTED_IMAGES.keys():
                    response = {
                        'error': True,
                        'msg': 'Image type not supported (must be .jpg, .png or .jpeg)',
                    }
                    return JsonResponse(response, status=400)
                elif img_content_type not in settings.WHITELISTED_IMAGES.values():
                    response = {
                        'error': True,
                        'msg': 'Image type not supported',
                    }
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

