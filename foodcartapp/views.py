from itertools import groupby
from operator import itemgetter

from django.db import transaction
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework import serializers

from .models import Product, OrderItem, Order, RestaurantMenuItem


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

    data = serializer.validated_data

    order_items_fields = data['products']

    order_price = sum(
        [
            fields['product'].price * fields['quantity']
            for fields in order_items_fields
        ]
    )

    products_ids = [fields['product'].id for fields in order_items_fields]

    restaurant_with_products = [
        (order_id, [value['product_id'] for value in values])
        for order_id, values in
        groupby(
            (RestaurantMenuItem.objects.values('restaurant_id', 'product_id')
             .order_by('restaurant_id')
             .filter(availability=True)),
            key=itemgetter('restaurant_id')
        )
    ]

    selected_restaurant = None

    for restaurant_id, menu_products in restaurant_with_products:
        for order_product in products_ids:
            if order_product in menu_products:
                continue
            break
        else:
            selected_restaurant = restaurant_id
            break

    if selected_restaurant is None:
        raise NotFound(
            {'error': 'products: can\'t find restaurant for this order'},
        )

    order = Order.objects.create(
        firstname=data['firstname'],
        lastname=data['lastname'],
        phonenumber=data['phonenumber'],
        address=data['address'],
        price=order_price,
        restaurant_id=selected_restaurant
    )

    OrderItem.objects.bulk_create([
        OrderItem(order=order, **fields)
        for fields in order_items_fields
    ])

    return Response(OrderSerializer(order).data)
