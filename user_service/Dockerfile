# Stage 1: Build stage
FROM python:3.9-slim as builder

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Final stage
FROM python:3.9-slim

WORKDIR /app

# Copy installed dependencies from the builder stage
COPY --from=builder /usr/local/lib/python3.9/site-packages /usr/local/lib/python3.9/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . /app/

# Expose the port the app will run on
EXPOSE 5000

# Install Gunicorn (ensure it's available in the final stage)
RUN pip install --no-cache-dir gunicorn

# Run the app with Gunicorn (4 workers as an example)
COPY init_db.py /app/init_db.py
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Run the entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
