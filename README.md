# Биллинговая система

- Главный файл лучше назвать `billing` `client` 
- Написать бизнес логу `текстом`. т.е пользователь заходит туда происходит магия и тд 
- для брокера сообщений лучше делать метод `crown` который чекает выполнения таски и записывает результат в таблицу

https://dev.to/speaklouder/redis-on-your-local-machine-using-docker-a-step-by-step-guide-l62 
Запуск redis: `docker run -d --name redis -p 6379:6379 redis:latest`
Для перезапуска: `docker rm redis`

ИЛИ

Запуск redis: `docker-compose up -d`
Остановка redis: `docker-compose down`

Запуск worker: `python worker.py`
