FROM python:3.12.4-slim
WORKDIR /app
COPY . /app

# Install core dependencies.
RUN apt-get update && apt-get install -y libpq-dev build-essential

# Install production dependencies.
RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "-u", "main.py"]
