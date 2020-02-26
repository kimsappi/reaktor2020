FROM python:3.8-alpine

LABEL version="0.0.1"

RUN pip3 install --upgrade pip
RUN pip3 install flask

COPY . /app
WORKDIR /app

ADD . .

CMD ["python3", "app.py"]