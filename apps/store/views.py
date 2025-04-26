from django.http import JsonResponse

from apps.store.functions import store_tree
from apps.warehouse.enums import Status
from apps.warehouse.models import Category

# Create your views here.


def store_view(request):
    if request.method == 'GET':
        categ_queryset = Category.objects.filter(parent_id= None).exclude(status= Status.DELETED)
        data = store_tree(categ_queryset)
        response = {
            'store': data,
        }
        return JsonResponse(response, status= 200)
