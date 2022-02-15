import phonenumbers
from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from .models import Product, OrderProduct, Order


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


def validate_keys(data: dict, keys: list, error_message_begin=''):
    validate_data = {
        key: data.get(key) for key in keys
    }

    errored_keys = []

    for key, value in validate_data.items():
        if value is None or value == "":
            errored_keys.append(key)

    if errored_keys:
        return {
            'error': f'{error_message_begin}{", ".join(errored_keys)}: '
                     f'not presented or null or ""'
        }


@api_view(['POST'])
def register_order(request):
    data = request.data

    validate_error = validate_keys(
        data, ['firstname', 'lastname', 'phonenumber', 'address', 'products']
    )

    if validate_error is not None:
        return Response(
            validate_error,
            status=status.HTTP_400_BAD_REQUEST
        )

    bad_phone = False

    try:
        parsed_phone = phonenumbers.parse(
            data['phonenumber'],
            'RU'
        )
    except phonenumbers.NumberParseException:
        bad_phone = True
    else:
        if phonenumbers.is_valid_number(parsed_phone):
            data['phonenumber'] = parsed_phone
        else:
            bad_phone = True

    if bad_phone:
        return Response(
            {'error': f'phonenumber: is not a phone number'},
            status=status.HTTP_400_BAD_REQUEST
        )

    order = Order(
        first_name=data['firstname'],
        last_name=data['lastname'],
        phone=data['phonenumber'],
        address=data['address']
    )

    products = data['products']

    if not isinstance(products, list):
        return Response(
            {'error': f'products: expected a list, got a {type(products)}'}
        )

    if not products:
        return Response(
            {'error': f'products: does not contain any value'}
        )

    order_products = []

    for num, order_item in enumerate(products):
        error_message_begin = f'products[{num}]: '

        validate_error = validate_keys(
            order_item,
            ['product', 'quantity'],
            error_message_begin=error_message_begin
        )

        if validate_error is not None:
            return Response(
                validate_error,
                status=status.HTTP_400_BAD_REQUEST
            )

        product_id = order_item['product']
        if not isinstance(product_id, int):
            return Response(
                {'error': f'{error_message_begin}product: '
                          f'expected a int, got a {type(products)}'}
            )
        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': f'{error_message_begin}product: '
                          f'{product_id} is not a valid product'}
            )

        quantity = order_item['quantity']
        if not isinstance(quantity, int):
            return Response(
                {'error': f'{error_message_begin}quantity: '
                          f'expected a int, got a {type(products)}'}
            )
        if quantity < 1:
            return Response(
                {'error': f'{error_message_begin}quantity: '
                          f'{quantity} is not a valid quantity'}
            )

        order_product = OrderProduct(
            order=order,
            product=product,
            quantity=quantity
        )

        order_products.append(order_product)

    order.save()
    for order_product in order_products:
        order_product.save()

    return Response({})
