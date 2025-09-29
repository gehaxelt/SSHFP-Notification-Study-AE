FROM python:3.11

WORKDIR /usr/src/app

RUN apt update
RUN apt install -y openssh-client

COPY ./app/requirements.txt /tmp/
RUN pip install --no-cache-dir -r /tmp/requirements.txt

CMD [ "python", "./app.py" ]
