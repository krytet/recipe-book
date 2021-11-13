FROM python:3.8.5

RUN mkdir /code
WORKDIR /code
COPY dump.json .
COPY requirements.txt .
COPY manage.py .
RUN pip3 install -r requirements.txt
COPY . .
CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000 