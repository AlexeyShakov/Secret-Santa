# Secret-Santa

## Описание проекта
Данный бот предназначен для игры в Тайного Санту. Для ознакомления с функциями бота
следует ввести /help в чате, либо выбрать в меню кнопку "Узнать информацию о боте".

## Структура .env

TG_BOT_TOKEN - токен бота, полученный у BotFather;

DB_HOST - хост, где расположена БД. В данном случае это название сервиса в docker-compose.yml;

DB_NAME - название БД, можете придумать любой;

DB_USER - имя юзера БД;

DB_PASS - пароль юзера БД;

DB_PORT - порт БД.

## Разворачивание проекта
На Вашем компьютере должен быть установлен Docker. После этого в корне проекта(там где лежит .env и main.py) в консоли нужно ввести команду 
```docker-compose up --build``` при первом поднятии проекта, после этого можно поднимать сервис с помощью ```docker-compose up```
