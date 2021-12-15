FROM python:3

EXPOSE 80
VOLUME [ "/attachments" ]

WORKDIR /app

RUN pip install poetry

COPY . .
COPY .env .env

RUN poetry install
RUN sed -i s/_dev//g .env
RUN poetry run aerich upgrade

CMD [ "poetry", "run", "uvicorn", "main:app", "--host", "localhost", "--port", "80" ]