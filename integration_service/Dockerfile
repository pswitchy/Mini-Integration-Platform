FROM python:3.9-slim

WORKDIR /code

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY ./integration_service/service /code/service

CMD ["python", "service/poller.py"]