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
