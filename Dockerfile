FROM python:3.9-bullseye

EXPOSE 80

WORKDIR /app

RUN apt-get update
RUN apt-get install -y ffmpeg
RUN pip install poetry

COPY . /app

RUN poetry install

COPY .env /app/.env
RUN sed -i s/_dev//g .env

RUN poetry run aerich upgrade

RUN mkdir uploads

VOLUME [ "/attachments" ]
CMD [ "poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80" ]