FROM ubuntu

RUN apt-get update -y && \
    apt-get install -y python3-pip python3-dev git && \
    apt-get clean

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r requirements.txt

COPY . /app

CMD [ "python", "app.py" ]
