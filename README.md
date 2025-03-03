# Blog

## Стек

<ul>
  <li>Ubuntu 24.04</li>
  <li>Docker 27.5.1</li>
  <li>Python 3.12</li>
  <li>Django 5.1.4</li>
  <li>Gunicorn 23.0.0</li>
  <li>Nginx 1.24.0</li>
</ul>

## Локальная инсталяция

Клонируйте репозиторий:
```sh
git clone https://github.com/galsrv/blog.git
```
Установите локальное окружение:
```sh
python -m venv venv
```
Активируйте локальное окружение:
```sh
. venv/bin/activate
```
Установите зависимости:
```sh
pip install -r backend/requirements.txt
```
Заполните файл с переменными окружения (.env) на основании примера (.env.example) 


## Инсталяция на новой виртуальной машине

На виртуальной машине должен быть установлен Docker.
Инсталяция ведется с помощью образов Docker, размещенных на Docker Hub.

В папку проекта следует разместить файлы:
<ul>
  <li><b>docker-compose.production.yml</b> - конфигурация для Docker Compose</li>
  <li><b>.env</b> - переменные окружения</li>
</ul>

Для развертывания контейнеров выполните команду:
```sh
docker compose -f docker-compose.production.yml up -d
```

Пример заполнения файла .env приведен в файле .env.example

## Деплой нового сборки на виртуальную машину

Остановить и удалить контейнеры:
```sh
docker compose -f docker-compose.production.yml down
```
Тома и их содержимое при этом сохраняются (при сохранении настроек .yml-файла)

Перезагрузить ВМ в случае изменения переменных окружения.

Принудительно обновить образы из хаба, собрать из них контейнеры и запустить в фоновом режиме:
```sh
docker compose -f docker-compose.production.yml up -d --pull always
```
Выполнить миграции в случае изменения структуры базы данных.

## Структура Docker

<ul>Используются тома:
  <li><b>db_blog_data</b> - база данных</li>
  <li><b>media</b> - загруженные пользователем файлы</li>
  <li><b>static</b> - статические файлы (админка Django)</li>
</ul>

<ul>Используются контейнеры:
  <li><b>blog_db</b> - PostgreSQL</li>
  <li><b>blog_backend</b> - Django-приложение + Gunicorn</li>
  <li><b>blog_gateway</b> - Nginx</li>
</ul>

## Дополнительные действия

При разворачивании на новом хосте дополнительно выполнить следующие действия

Выполнить миграции:
```sh
python manage.py migrate
```
Создать суперпользователя:
```sh
python manage.py createsuperuser
```
Собрать статику в папку STATIC_ROOT:
```sh
python manage.py collectstatic
```

## Nginx

На виртуальной машине должен быть установлен Nginx.
Файл конфигурации Nginx (default) сохранен в корне проекта.

Nginx должен слушать порт 443 и транслировать запрос на порт 8000 локалхоста.
Docker пробрасывает порт 8000 локалхоста на порт 80 контейнера с Nginx.
Nginx в контейнере слушает порт 80 хоста и транслирует запрос на порт 8000 контейнера бэкенда.
Сервер бэкенда (gunicorn) принимает запросы на 8000 порту.  

Nginx в контейнере раздает статику с адресов media/ и static/

## SSL

SSL-сертификат выдан Let’s Encrypt и автоматически обновляется каждые 90 дней через бот certbot.

Проверить статус сертификата:
```sh
sudo certbot certificates
```
Обновление вручную
```sh
sudo certbot renew --pre-hook "service nginx stop" --post-hook "service nginx start"
```

## REST API

Энд поинты перечислены в двух форматах на страницах swagger/ и redoc/

## Области для развития

<ul>
  <li>Добавить процесс CI/CD</li>
  <li>BUG - при создании суперюзера не создается запись в таблице Blogger</li>
  <li>BUG - при создании через API не создается запись в таблице Blogger </li>
  <li>NICE TO HAVE - Навести порядок с именами url</li>
  <li>NICE TO HAVE - Отключать троттлинг во время тестов</li>
</ul>