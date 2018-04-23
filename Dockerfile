FROM python:3.6.4-alpine3.7

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY prom_eureka.py ./

CMD [ "python", "./prom_eureka.py" ]
