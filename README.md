# Drbnatell 💬

Jak nasadit:

```bash
docker build -t drbnatell .

docker run -d -v $(pwd)/attachments:/app/attachments -p $PORT:80 --name drbnatell drbnatell
```