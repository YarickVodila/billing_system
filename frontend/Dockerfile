FROM python:3.11-slim-buster

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt
# RUN python create_db
# COPY . .

EXPOSE 8001

CMD ["streamlit", "run", "streamlit_app.py", "--server.port", "8001"]
