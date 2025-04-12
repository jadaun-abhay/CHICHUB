from django.conf import settings

from apps.warehouse.enums import Status
from apps.warehouse.models import Category

from utils.functions import encode


def categ_path_generator(categ_id, include_self= True):
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
                'error': True,
                'msg': 'Image type not supported (must be .jpg, .png or .jpeg)',
            }
            return response
        elif img_content_type not in settings.WHITELISTED_IMAGES.values():
            response = {
                'error': True,
                'msg': 'Image type not supported',
            }
            return response
    return True