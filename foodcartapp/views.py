from django.db import transaction
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import serializers

from .models import Product, OrderItem, Order


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            },
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('product', 'quantity')


class OrderSerializer(serializers.ModelSerializer):
    products = serializers.ListField(
        child=OrderItemSerializer(),
        allow_empty=False,
        write_only=True
    )

    class Meta:
        model = Order
        fields = (
            'firstname',
            'lastname',
            'phonenumber',
            'address',
            'products'
        )


@api_view(['POST'])
@transaction.atomic
def register_order(request):
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    order_description = serializer.validated_data

    order_items_fields = order_description['products']

    for fields in order_items_fields:
        fields['price_at_order'] = fields['product'].price

    order = Order.objects.create(
        firstname=order_description['firstname'],
        lastname=order_description['lastname'],
        phonenumber=order_description['phonenumber'],
        address=order_description['address']
    )

    OrderItem.objects.bulk_create([
        OrderItem(order=order, **fields)
        for fields in order_items_fields
    ])

    return Response(OrderSerializer(order).data)
