FROM python:3

WORKDIR /app

ADD ./requirements.txt /app/

RUN pip install -r requirements.txt

ADD ./src/* /app/

ENTRYPOINT [ "python" ]
