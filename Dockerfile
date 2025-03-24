FROM python:3.12.4-slim
WORKDIR /app
COPY . /app

CMD ["./venv/Scripts/activate", "&", "py", "-u", "app/src/main.py"]
