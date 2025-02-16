# Blog


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
В файле с переменными окружения установите 
```python
DB_HOST='127.0.0.1'
```
По желанию установите
```python
DEBUG=True
```

## Инсталяция через Docker

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

Образы хранятся на DockerHub

## Дополнительные действия

При разворачивании на новом сервере дополнительно выполнить следующие действия

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