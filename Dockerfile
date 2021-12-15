FROM python:3

EXPOSE 80

WORKDIR /app

RUN pip install poetry

COPY . /app

RUN poetry install
RUN sed -i s/_dev//g .env
RUN poetry run aerich upgrade

COPY .env /app/.env

VOLUME [ "/attachments" ]
CMD [ "poetry", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80" ]