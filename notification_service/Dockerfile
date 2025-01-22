# Stage 1: Build stage
FROM python:3.9-slim as builder

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final stage
FROM python:3.9-slim

WORKDIR /app
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY . /app/

EXPOSE 5002
CMD ["python", "app.py"]
