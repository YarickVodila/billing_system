from tasks import app_celery

if __name__ == '__main__':
    # Запуск воркера с одним процессом (для Windows)
    app_celery.worker_main(
        argv=['worker', '--pool=solo', '--loglevel=info']
    )