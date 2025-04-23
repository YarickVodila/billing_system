from tasks import app

if __name__ == '__main__':
    # Запуск воркера с одним процессом (для Windows)
    app.worker_main(
        argv=['worker', '--pool=solo', '--loglevel=info']
    )