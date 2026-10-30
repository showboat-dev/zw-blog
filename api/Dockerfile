FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml .
COPY app ./app
COPY seed.py ./seed.py
COPY entrypoint.sh ./entrypoint.sh
RUN pip install --no-cache-dir . && chmod +x entrypoint.sh

EXPOSE 8000
CMD ["./entrypoint.sh"]
