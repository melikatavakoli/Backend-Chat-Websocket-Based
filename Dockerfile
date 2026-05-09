FROM docker.arvancloud.ir/python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

ENV DJANGO_SETTINGS_MODULE=config.settings

EXPOSE 8000

CMD ["/app/entrypoint.sh"]
