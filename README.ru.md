# tg-spotify

## Описание
tg-spotify - это проект, который обновляет ваш био в Telegram в соответствии с текущим состоянием воспроизведения Spotify.

## Требования
- Docker

## Установка
1. Клонируйте репозиторий:
    ```sh
    git clone https://github.com/Laefye/tg-spotify.git
    cd tg-spotify
    ```

2. Соберите и запустите контейнер Docker:
    ```sh
    docker build -t tg-spotify . 
    docker run -it --name tg-spotify -v /path/to/local/storage:/app/storage tg-spotify
    ```
    Примечание: Флаг `-it` используется для интерактивного создания файла конфигурации. После настройки конфигурации вы можете запустить контейнер без `-it`:
    ```sh
    docker start tg-spotify
    ```

## Использование
Чтобы (пере)создать файл конфигурации, вам нужно настроить конфигурацию:
```sh
docker exec -it tg-spotify /app/venv/bin/python3 main.py generate
```

## Примечание
Нативная поддержка Windows (без Docker) не предусмотрена.

## Настройка
Чтобы изменить шаблон био, измените файл `formating.py`. Функция `format` отвечает за генерацию текста био на основе текущего состояния воспроизведения.