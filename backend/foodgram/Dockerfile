FROM python:3.8.5

#RUN mkdir /code
WORKDIR /code
#COPY requirements.txt .
RUN echo "PWD is: $PWD"
RUN echo "ls is: $LS"
COPY . .
RUN pip3 install -r requirements.txt
CMD gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000 