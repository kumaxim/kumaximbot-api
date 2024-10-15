# API of Telegram Bot @kumaximbot

[![Yandex Function](https://github.com/kumaxim/kumaximbot-api/actions/workflows/main.yml/badge.svg)](https://github.com/kumaxim/kumaximbot-api/actions/workflows/main.yml)

API Telegram бота [@kumaximbot](https://t.me/kumaximbot). Использованные технологии: 
[Python](https://www.python.org/)(3.12) | [Poetry](https://python-poetry.org/) | 
[FastAPI](https://fastapi.tiangolo.com/) | [Aioogram](https://docs.aiogram.dev/en/latest/) |
[SQLAlchemy](https://www.sqlalchemy.org/) | [Alembic](https://alembic.sqlalchemy.org/en/latest/).


## Демо
Telegram bot: [@kumaximbot](https://t.me/kumaximbot) | 
OpenAPI схема: [swagger-ui](https://d5djd46lehb5f0u4atqk.apigw.yandexcloud.net/docs) |
Интерфейс: [web-client](https://kumaximbot-ui.website.yandexcloud.net/)

## Системные требования
- ОС: Debian 11 / 12 или Ubuntu 22.04 / 24.04
- Среда исполнения: Python 3.12
- Менеджер пакетов: Poetry 1.8.3


## Переменные окружения
Скопируйте содержимое [example.env](env.example) в файл `.env` либо добавьте соответсвующее переменные в окружение: 
```shell
# Установить уровень вывода сообщений в режим DEBUG и выводить исполняемые запросы в консоль  
DEV_MODE = False
# Токен Telegram бота из @BotFather
BOT_TOKEN = "<tg-bot-token>"
# Секретный токен, который будет передавать Telegram при обращениях к webhook в заголовке "X-Telegram-Bot-Api-Secret-Token"
TELEGRAM_SECRET_TOKEN = "<tg-api-secret-token>"
# Client ID приложения oauth.yandex.ru
YANDEX_OAUTH_CLIENT_ID = "<oauth-client-id>"
# Client secret приложения oauth.yandex.ru
YANDEX_OAUTH_CLIENT_SECRET = "<oauth-client-secret>"
# Логин пользователя - администратора 
PRIVILEGED_USER_LOGIN = "<username>"
```

*Замечание*: в качестве сервера авторизации в проекте используется Yandex ID.  Для того чтобы взаимодействовать с ним,
необходимо зарегистрировать приложение, согласно [документации](https://yandex.ru/dev/id/doc/ru/). Затем, переменной
`PRIVILEGED_USER_LOGIN` необходимо установить значение равное Вашему логину на Яндексе. Обязательно в *нижнем* регистре.
Таким образом, любой пользователь сможет пройти авторизацию, но не будет иметь возможности добавлять/редактировать сообщения,
отправляемые Telegram ботом. Подробнее о том, какие именно методы API защищены таким образом, смотрите в
[openapi](https://d5djd46lehb5f0u4atqk.apigw.yandexcloud.net/docs) схеме.

## Установка и запуск
```shell
poetry install
poetry shell
alembic upgrade head 
python -m app.tgbot.bot # Для запуска Telegram бота в polling mode
python -m uvicorn app.main:app--reload --host localhost # Для запуска FastAPI
```

## Развёртывание
Развертывание приложения осуществляется на инфраструктуре Яндекс облака с использованием следующих сервисов:
[Cloud Functions](https://yandex.cloud/ru/docs/functions/) | 
[API Gateway](https://yandex.cloud/ru/docs/api-gateway/) |
[Lockbox](https://yandex.cloud/ru/docs/lockbox/) |
[Object storage](https://yandex.cloud/ru/docs/storage/) |
[Identity and Access Management](https://yandex.cloud/ru/docs/iam/).
Их настройка и конфигурация осуществляется при помощи [Terraform](https://www.terraform.io/) и описана в файле [yc.tf](yc.tf).
Для полноты картины, также можно ознакомиться с [файлом](.github/workflows/main.yml) настройки окружения GitHub Actions. 

Для того чтобы запустить имеющуюся конфигурацию Terraform, необходимо:
1. Создать сервисный аккаунт в сервисе [Identity and Access Management](https://yandex.cloud/ru/docs/iam/)
2. Установить и выполнить инициализацию утилиты [YC CLI](https://yandex.cloud/ru/docs/cli/quickstart) 
3. Установить Terraform и настроить провайдер, в соответствии с [инструкцией](https://yandex.cloud/ru/docs/tutorials/infrastructure-management/terraform-quickstart)
4. Создать авторизованный ключ для сервисного аккаунта: `yc iam key create --service-account-id <id-сервисного-аккаунта> --output key.json`
5. Установить переменные окружения со следующими значениями:
   - `YC_SERVICE_ACCOUNT_KEY_FILE` - путь к файлу с ключом сервисного аккаунта или строка с его содержимым
   - `YC_CLOUD_ID` - идентификатор облака
   - `YC_FOLDER_ID` - идентификатор каталога
6. Назначить сервисному аккаунту следующие права на каталог:
   - `storage.editor`
   - `functions.editor`
   - `iam.serviceAccounts.user`
   - `lockbox.payloadViewer`
   - `iam.serviceAccounts.accessKeyAdmin`
   - `api-gateway.editor`
   - `lockbox.editor`
7. Настроить backend для хранения состояний Terraform:
    - Создать s3 backet
    - Создать сервисный аккаунт и статический ключ доступа для него
    - Назначить сервисный аккаунт на s3 backet с ролью `storage.editor`
    - Добавить переменные окружения со следующими значениями:
      - `YC_BACKEND_ACCESS_KEY` - идентификатор ключа
      - `YC_BACKEND_SECRET_KEY` - секретный ключ
    - Инициализировать backend: `terraform init -backend-config="access_key=$YC_BACKEND_ACCESS_KEY" -backend-config="secret_key=$YC_BACKEND_SECRET_KEY"`
8. Установить зависимости проекта: `poetry install`
9. (Опционально) Скачать содержимое s3 бакета, в котором хранятся статические файлы(sqlite, pdf) проекта:
   - Установить и настроить `aws cli` в соответствии с [инструкцией](https://yandex.cloud/ru/docs/storage/tools/aws-cli)
   - Скачать все содержимое в папку `./assets/`: `aws s3 cp s3://<backet_name> ./assets/ --recursive --endpoint-url=https://storage.yandexcloud.net`
10. Применить миграции: `poetry run alembic upgrade head` 
11. Экспортировать зависимости в файл `requirements.txt`: `poetry export -o requirements.txt --without-hashes --without=dev`
12. Пробросить значения переменных окружения из [секции](#переменные-окружения) выше в Terraform при помощи суффикса `TF_VAR_`:
    - `TF_VAR_BOT_TOKEN` = `$BOT_TOKEN`
    - `TF_VAR_TELEGRAM_SECRET_TOKEN` = `$TELEGRAM_SECRET_TOKEN`
    - `TF_VAR_YANDEX_OAUTH_CLIENT_ID` = `$YANDEX_OAUTH_CLIENT_ID`
    - `TF_VAR_YANDEX_OAUTH_CLIENT_SECRET` = `$YANDEX_OAUTH_CLIENT_SECRET`
    - `TF_VAR_PRIVILEGED_USER_LOGIN` = `$PRIVILEGED_USER_LOGIN`
13. Добавить переменную окружения `TF_VAR_SERVICE_ACCOUNT_ID` со значением идентификатора сервисного аккаунта из п.1
14. Сгенерировать план выполнения: `terraform plan -out=cf2plan`
15. Создать и/или обновить инфраструктуру проекта: `terraform apply cf2plan`
    

## Лицензия

Проект размещен на условиях лицензии MIT


## Автор

Кудрявцев Максим - [kumaxim](https://github.com/kumaxim). 2024 год.
