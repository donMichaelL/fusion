FROM python:3.8-slim-buster

LABEL maintener="Michael Loukeris"

ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1


RUN apt-get update && apt-get install nano

RUN mkdir /code

WORKDIR /code

COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt

COPY . .

CMD [ "python", "consumer.py" ]
