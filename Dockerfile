FROM python:3.6-stretch
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
COPY requirements.txt /code
WORKDIR /code
ADD . /code/
RUN mkdir -p /code/logs

RUN pip install -r requirements.txt
EXPOSE 8000
