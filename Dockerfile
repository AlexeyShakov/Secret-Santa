FROM python:3.10

RUN mkdir /secret_santa

WORKDIR  /secret_santa

COPY requirements.txt /secret_santa

ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
RUN apt update && apt install -y gettext && apt install netcat-traditional

RUN pip install -r /secret_santa/requirements.txt

COPY . .

RUN chmod +x /secret_santa/entrypoint.sh