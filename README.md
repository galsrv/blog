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