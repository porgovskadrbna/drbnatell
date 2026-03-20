FROM python:3.14-trixie

EXPOSE 80

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg
RUN pip install uv

COPY . /app

RUN uv sync

VOLUME [ "/app/data", "/app/.env" ]
CMD [ "uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80" ]
