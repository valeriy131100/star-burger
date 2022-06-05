# Сайт доставки еды Star Burger

Это сайт сети ресторанов Star Burger. Здесь можно заказать превосходные бургеры с доставкой на дом.

![скриншот сайта](https://dvmn.org/filer/canonical/1594651635/686/)


Сеть Star Burger объединяет несколько ресторанов, действующих под единой франшизой. У всех ресторанов одинаковое меню и одинаковые цены. Просто выберите блюдо из меню на сайте и укажите место доставки. Мы сами найдём ближайший к вам ресторан, всё приготовим и привезём.

На сайте есть три независимых интерфейса. Первый — это публичная часть, где можно выбрать блюда из меню, и быстро оформить заказ без регистрации и SMS.

Второй интерфейс предназначен для менеджера. Здесь происходит обработка заказов. Менеджер видит поступившие новые заказы и первым делом созванивается с клиентом, чтобы подтвердить заказ. После оператор выбирает ближайший ресторан и передаёт туда заказ на исполнение. Там всё приготовят и сами доставят еду клиенту.

Третий интерфейс — это админка. Преимущественно им пользуются программисты при разработке сайта. Также сюда заходит менеджер, чтобы обновить меню ресторанов Star Burger.

## Как запустить dev-версию сайта

Вам понадобится установленные git, [Docker](https://docs.docker.com/get-docker/) и [Docker Compose](https://docs.docker.com/compose/install/).

Склонируйте репозиторий:
```bash
git clone https://github.com/valeriy131100/star-burger
```

Подготовьте `.env` файл с настройками:
- `YANDEX_GEOCODER_API_KEY` - ключ API от геокодера Яндекса. Создать можно [здесь](https://developer.tech.yandex.ru/services/). Вам необходим "JavaScript API и HTTP Геокодер".
- `ROLLBAR_TOKEN` - токен доступа от [Rollbar](https://rollbar.com/).
- `ROLLBAR_ENVIRONMENT` - название окружения для [Rollbar](https://rollbar.com/).

Доступны и прочие настройки из prod-версии.

Соберите проект:
```bash
docker-compose build
```

Запустите сайт:
```bash
docker-compose up -d
```

Перейдите в контейнер и запустите миграции:
```bash
docker-compose exec backend python manage.py migrate
```

Сайт будет доступен по адресу [127.0.0.1:8080](http://127.0.0.1:8080).

## Как запустить prod-версию сайта

Координаты prod-сервера:
* Domain - [starburger.efremov.xyz](https://starburger.efremov.xyz)
* IP - 45.132.18.71
* User - root
* Местоположение сайта - /opt/star-burger

Вам понадобится установленные git, [Docker](https://docs.docker.com/get-docker/) и [Docker Compose](https://docs.docker.com/compose/install/).

Склонируйте репозиторий:
```bash
git clone https://github.com/valeriy131100/star-burger
```

Подготовьте `.env` файл с настройками:
- `DEBUG` — дебаг-режим. Поставьте `False`.
- `SECRET_KEY` — секретный ключ проекта. Он отвечает за шифрование на сайте. Например, им зашифрованы все пароли на вашем сайте. Не стоит использовать значение по-умолчанию, **замените на своё**.
- `ALLOWED_HOSTS` — [см. документацию Django](https://docs.djangoproject.com/en/3.1/ref/settings/#allowed-hosts)
- `DATABASE` — строка подключения к базе данных в формате [dj-database-url](https://github.com/jacobian/dj-database-url#url-schema).
- `YANDEX_GEOCODER_API_KEY` - ключ API от геокодера Яндекса. Создать можно [здесь](https://developer.tech.yandex.ru/services/). Вам необходим "JavaScript API и HTTP Геокодер".
- `ROLLBAR_TOKEN` - токен доступа от [Rollbar](https://rollbar.com/).
- `ROLLBAR_ENVIRONMENT` - название окружения для [Rollbar](https://rollbar.com/).
- `POSTGRES_USER` - имя пользователя для создаваемой базы данных.
- `POSTGRES_PASSWORD` - пароль пользователя для создаваемой базы данных.
- `POSTGRES_DB` - название создаваемой базы данных.

Соберите проект:
```bash
docker-compose -f docker-compose.prod.yml build
```

Запустите сайт:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

Если вы предварительно не настроили ключи Let's Encrypt, то сайт, вероятно, упадет.

Наиболее простой способ - получить их изначально любым способом, а затем скопировать папку LE в volume `star-burger_certbot-etc`.
```bash
docker inspect star-burger_certbotetc
```
Скопируйте путь из Mountpoint, а затем исполните:
```
cp -r /etc/letsencrypt/* {путь до volume}
```

После того как сайт запустится примените миграции:
```bash
docker-compose -f docker-compose.prod.yml exec backend python manage.py migrate
```

Также в папке проекта есть скрипт для обновления сертификатов `ssl_renew`. Добавьте его в crontab или любой другой способ периодического запуска задач. Отредактируйте пути до файлов, если они у вас отличаются.

## Как быстро обновить сайт

Обновите версию кода:
```bash
git pull
```

Соберите новую версию:
```bash
docker-compose -f docker-compose.prod.yml build
```

Запустите сайт:
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Цели проекта

Код написан в учебных целях — это урок в курсе по Python и веб-разработке на сайте [Devman](https://dvmn.org). За основу был взят код проекта [FoodCart](https://github.com/Saibharath79/FoodCart).

Где используется репозиторий:

- Второй и третий урок [учебного модуля Django](https://dvmn.org/modules/django/)
