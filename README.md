Портал обмена

1. создайте файл .env.dev в директории apps  
SECRET_KEY='секретный ключ джанго'  
ALLOWED_HOSTS=localhost 127.0.0.1  
CSRF_TRUSTED_ORIGINS=http://localhost:8001  
POSTGRES_USER=django  
POSTGRES_PASSWORD=password  
POSTGRES_DB=apps  
POSTGRES_PORT=5432  

  


2. Запускаем приложение docker compose up
3. Переходим по адресу http://localhost:8001/ads
             
Создан пользователь admin (пароль-admin)  
А такде пользователь 1234@mail.ru (пароль qwer1234)  
Также же вы можете сами зарегистрироваться  

Если вы хотите заполнить базу данных самостоятельно,  
то удалите директорию data (это база данных)
