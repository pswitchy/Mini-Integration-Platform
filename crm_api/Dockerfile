FROM python:3.9-slim

WORKDIR /code

COPY ./requirements.txt . 
RUN pip install --no-cache-dir -r requirements.txt

COPY ./crm_api/app /code/app

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]