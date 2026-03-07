FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (layer caching)
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY src/ /app

ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["python", "__main__.py", "--host", "0.0.0.0", "--port", "5000"]
