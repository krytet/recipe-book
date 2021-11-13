FROM python:3.8.5

RUN mkdir /code
WORKDIR /code
CMD ls
COPY ./requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000 