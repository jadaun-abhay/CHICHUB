from apps.store.aggregates import GroupConcat
from apps.warehouse.enums import Status
from apps.warehouse.models import Category, CategoryImages, Product

from utils.functions import encode


def store_tree(queryset):
    result = []
    for category in queryset:
        children_queryset = Category.objects.filter(parent_id= category.id).exclude(status= Status.DELETED)
        products_queryset = Product.objects.filter(category= category).exclude(status= Status.DELETED).values('id', 'name', 'description', 'category_id', 'price_per_unit', 'stocks_available', 'prod_status', 'discount').annotate(images= GroupConcat('images__image'))
        [product.update({'id': encode(product.get('id'))}) for product in products_queryset]
        result.append(
            {
                'id': encode(category.id),
                'name': category.name,
                'description': category.description,
                'pid': category.parent_id,
                'discount': category.discount,
                'children': list(store_tree(children_queryset)),
                'products': list(products_queryset),
                'images': list(CategoryImages.objects.filter(category= category).values_list('image', flat= True)),
            }
        )
    return result
