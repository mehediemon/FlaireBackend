#!/bin/bash
# Initialize the database
python /app/init_db.py

# Start the Gunicorn server
exec gunicorn --workers 4 --bind 0.0.0.0:5000 app:app
