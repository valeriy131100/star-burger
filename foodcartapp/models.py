from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class Order(models.Model):
    FINISHED_STATUS = (
        'completed', 'rejected', 'failed'
    )

    address = models.CharField(
        max_length=200,
        verbose_name='адрес',
        db_index=True
    )

    firstname = models.CharField(
        max_length=100,
        verbose_name='имя',
        db_index=True
    )
    lastname = models.CharField(
        max_length=100,
        verbose_name='фамилия',
        db_index=True
    )

    phonenumber = PhoneNumberField(
        verbose_name='телефон',
        db_index=True
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='цена',
        db_index=True,
        validators=[MinValueValidator(0)]
    )

    status = models.CharField(
        max_length=50,
        verbose_name='статус',
        db_index=True,
        choices=(
            ('unperformed', 'Необработанный'),
            ('in work', 'В работе'),
            ('delivery', 'Доставляется'),
            ('completed', 'Выполнен'),
            ('rejected', 'Отменен'),
            ('failed', 'Завершен неудачно')
        ),
        default='unperformed'
    )

    comment = models.TextField(
        verbose_name='комментарий',
        db_index=True,
        blank=True
    )

    registered_at = models.DateTimeField(
        verbose_name='когда зарегистрирован',
        db_index=True,
        default=timezone.now
    )

    called_at = models.DateTimeField(
        verbose_name='когда сделан звонок',
        db_index=True,
        null=True,
        blank=True
    )

    delivered_at = models.DateTimeField(
        verbose_name='когда доставлен',
        db_index=True,
        null=True,
        blank=True
    )

    pay_by = models.CharField(
        max_length=50,
        verbose_name='способ оплаты',
        choices=(
            ('cash', 'Наличностью'),
            ('card', 'Электронно'),
            ('not chose', 'Не выбран')
        ),
        default='not chose',
        db_index=True
    )

    restaurant = models.ForeignKey(
        Restaurant,
        verbose_name='ресторан',
        related_name='orders',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=True
    )

    class Meta:
        verbose_name = 'заказ'
        verbose_name_plural = 'заказы'

    def __str__(self):
        return f'Заказ на {self.address}'


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name='заказ'
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='orders_positions',
        verbose_name='продукт'
    )
    quantity = models.PositiveIntegerField(
        verbose_name='количество'
    )

    class Meta:
        verbose_name = 'заказанный продукт'
        verbose_name_plural = 'заказанные продукты'
        unique_together = (
            ('order', 'product'),
        )

    def __str__(self):
        return f'{self.product} ({self.quantity} шт.) в заказе {self.order.id}'
