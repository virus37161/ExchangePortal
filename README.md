Портал обмена

создайте файл .env.dev в директории shop
SECRET_KEY='секретный ключ джанго'
ALLOWED_HOSTS=localhost 127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8001
POSTGRES_USER=django
POSTGRES_PASSWORD=password
POSTGRES_DB=apps
POSTGRES_PORT=5432


Запускаем приложение docker compose up
Переходим по адресу http://localhost:8001/ads
Вы можете зарегистрироваться

Но если вам лень это делать, то
можете воспользоваться админом (логин и пароль - admin)

Если вы хотите заполнить портал самостоятельно,
то удалите директорию data (это база данных)

после чего в контейнере apss-1 создайте пользователя admin (python manage.py createsuperuser)
