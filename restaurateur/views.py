from itertools import groupby
from operator import attrgetter

import geopy.distance
from django import forms
from django.conf import settings
from django.shortcuts import redirect, render
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login
from django.contrib.auth import views as auth_views
from rest_framework import serializers

from addresses.models import Address
from foodcartapp.models import Product, Restaurant, Order, RestaurantMenuItem


class Login(forms.Form):
    username = forms.CharField(
        label='Логин', max_length=75, required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Укажите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль', max_length=75, required=True,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Введите пароль'
        })
    )


class LoginView(View):
    def get(self, request, *args, **kwargs):
        form = Login()
        return render(request, "login.html", context={
            'form': form
        })

    def post(self, request):
        form = Login(request.POST)

        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                if user.is_staff:  # FIXME replace with specific permission
                    return redirect("restaurateur:RestaurantView")
                return redirect("start_page")

        return render(request, "login.html", context={
            'form': form,
            'ivalid': True,
        })


class LogoutView(auth_views.LogoutView):
    next_page = reverse_lazy('restaurateur:login')


def is_manager(user):
    return user.is_staff  # FIXME replace with specific permission


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_products(request):
    restaurants = list(Restaurant.objects.order_by('name'))
    products = list(Product.objects.prefetch_related('menu_items'))

    default_availability = {restaurant.id: False for restaurant in restaurants}
    products_with_restaurants = []
    for product in products:
        availability = {
            **default_availability,
            **{item.restaurant_id: item.availability for item in product.menu_items.all()},
        }
        orderer_availability = [availability[restaurant.id] for restaurant in restaurants]

        products_with_restaurants.append(
            (product, orderer_availability)
        )

    return render(request, template_name="products_list.html", context={
        'products_with_restaurants': products_with_restaurants,
        'restaurants': restaurants,
    })


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_restaurants(request):
    return render(request, template_name="restaurants_list.html", context={
        'restaurants': Restaurant.objects.all(),
    })


class OrderSerializer(serializers.ModelSerializer):
    status = serializers.CharField(source='get_status_display')
    pay_by = serializers.CharField(source='get_pay_by_display')
    restaurants = serializers.SerializerMethodField()

    def get_restaurants(self, order: Order):
        addresses = self.context.get('addresses')

        order_coordinates = addresses.get(order.address)

        if order_coordinates is None:
            order_address = Address.objects.create(
                address=order.address
            )
            try:
                order_address.update_coordinates()
            except ValueError:
                # handle null coordinates later
                pass

            order_coordinates = order_address.coordinates
            addresses[order.address] = order_coordinates

        if order_coordinates == Address.NULL_COORDINATES:
            return 'Невозможный адрес заказа'

        products_ids = [
            order_item.product_id for order_item in order.products.all()
        ]

        grouped_menu_items = self.context.get('grouped_menu_items')

        selected_restaurants = []

        for restaurant, menu_items in grouped_menu_items:
            menu_products = [menu_item.product_id for menu_item in menu_items]
            if all(products_ids) in menu_products:
                selected_restaurants.append(restaurant)

        formatted_restaurants = []

        for restaurant in selected_restaurants:
            restaurant_coordinates = addresses.get(restaurant.address)
            if not restaurant_coordinates:
                restaurant_address = Address.objects.create(
                    address=restaurant.address
                )
                try:
                    restaurant_address.update_coordinates()
                except ValueError:
                    # handle null coordinates later
                    pass
                restaurant_coordinates = restaurant_address.coordinates
                addresses[restaurant.address] = restaurant_coordinates

            if restaurant_coordinates == Address.NULL_COORDINATES:
                formatted_restaurants.append(
                    f'{restaurant.name}: Невозможный адрес'
                )
                continue

            restaurant_distance = geopy.distance.distance(
                restaurant_coordinates,
                order_coordinates
            )

            formatted_restaurants.append(
                f'{restaurant.name}: {round(restaurant_distance.km, 2)}км'
            )

        return '\n'.join(formatted_restaurants)

    class Meta:
        model = Order
        fields = (
            'id',
            'firstname',
            'lastname',
            'phonenumber',
            'address',
            'price',
            'status',
            'comment',
            'pay_by',
            'restaurants'
        )


@user_passes_test(is_manager, login_url='restaurateur:login')
def view_orders(request):
    unfinished_orders = (Order.objects
                              .exclude(status__in=Order.FINISHED_STATUS)
                              .prefetch_related('products'))

    menu_items = (RestaurantMenuItem.objects
                                    .filter(availability=True)
                                    .select_related('restaurant')
                                    .order_by('restaurant_id'))

    grouped_menu_items = {
        restaurant: list(menu_items)
        for restaurant, menu_items in
        groupby(menu_items, attrgetter('restaurant'))
    }.items()

    restaurants = list(set([menu_item.restaurant for menu_item in menu_items]))

    restaurants_addresses = [restaurant.address for restaurant in restaurants]
    orders_addresses = [order.address for order in unfinished_orders]

    addresses = Address.objects.filter(
        address__in=restaurants_addresses + orders_addresses
    )

    context_addresses = {
        address.address: address.coordinates for address in addresses
    }

    return render(request, template_name='order_items.html', context={
        'orders': OrderSerializer(
            unfinished_orders,
            many=True,
            context={
                'grouped_menu_items': grouped_menu_items,
                'addresses': context_addresses
            }
        ).data
    })
