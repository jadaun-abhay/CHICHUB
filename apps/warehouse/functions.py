from django.conf import settings

from apps.warehouse.enums import Status
from apps.warehouse.models import Category, Product

from utils.functions import encode


def categ_path_generator(categ_id):
    path = ''
    path += f'{encode(categ_id)}/children/'
    queryset = Category.objects.filter(children= Category(categ_id)).exclude(status= Status.DELETED)
    for parent in queryset:
        parent_path = categ_path_generator(parent.id)
        path = f'{parent_path}'+path
    return path


def check_image_validity(images):
    for image in images:
        img_extension = image.name.split('.')[-1]
        img_content_type = image.content_type
        if img_extension not in settings.WHITELISTED_IMAGES.keys():
            response = {
                'file': image.name,
                'msg': 'Image type not supported (must be .jpg, .png or .jpeg)',
            }
            return response
        elif img_content_type not in settings.WHITELISTED_IMAGES.values():
            response = {
                'file': image.name,
                'msg': 'Image type not supported',
            }
            return response
    return True

def prod_path_generator(prod_id):
    path = ''
    parent_category_instance = Product.objects.filter(id= prod_id).select_related('category').first().category
    prod_path = "/".join(categ_path_generator(parent_category_instance.id).split("/")[:-2]) + f"/products/{encode(prod_id)}/"
    return prod_path
