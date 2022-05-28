FROM python:3.8.10

COPY requirements.txt  ./
COPY cats_vs_dogs_bot.py ./

RUN apt update &&\
    pip install --upgrade pip &&\
    pip install -r requirements.txt

CMD exec python cats_vs_dogs_bot.py