FROM python:3.8.5

#RUN mkdir /code
WORKDIR /code
#COPY requirements.txt .

COPY . .
RUN pip install -r requirements.txt
CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000 