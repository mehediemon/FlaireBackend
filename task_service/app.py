from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

app.config['SECRET_KEY'] = 'your_secret_key'

# PostgreSQL Configuration
DB_CONFIG = {
    'dbname': 'task_db',
    'user': 'test',
    'password': '12345678',
    'host': 'localhost',  # Change if using a remote database
    'port': 5432
}
DB_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'task_db'),
    'user': os.getenv('DB_USER', 'test'),
    'password': os.getenv('DB_PASSWORD', '12345678'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432))
}

# Notification service URL (for sending notifications to Telegram)
#NOTIFICATION_SERVICE_URL = "http://127.0.0.1:5002/notify"
NOTIFICATION_SERVICE_URL = os.getenv('NOTIFICATION_SERVICE_URL', 'http://127.0.0.1:5002/notify')
# Database connection helper
def get_db():
    return psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)

# Create tasks table if not exists
def create_table():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            user_email TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            completed BOOLEAN NOT NULL DEFAULT FALSE
        );
        ''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error creating table: {e}")

# Authenticate user based on JWT token
def authenticate(token):
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        return data['email']
    except Exception:
        return None

# Route to get tasks for the authenticated user
@app.route('/tasks', methods=['GET'])
def get_tasks():
    token = request.headers.get('Authorization', '').split(' ')[1]
    user = authenticate(token)
    if not user:
        return jsonify({'message': 'Unauthorized'}), 401

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE user_email = %s', (user,))
        tasks = cursor.fetchall()
        conn.close()
        return jsonify(tasks)
    except Exception as e:
        return jsonify({'message': 'Error fetching tasks', 'error': str(e)}), 500

# Route to create a new task
@app.route('/tasks', methods=['POST'])
def create_task():
    token = request.headers.get('Authorization', '').split(' ')[1]
    user = authenticate(token)
    if not user:
        return jsonify({'message': 'Unauthorized'}), 401

    data = request.json
    title = data.get('title')
    description = data.get('description')

    if not title or not description:
        return jsonify({'message': 'Title and description are required'}), 400

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO tasks (user_email, title, description, completed)
        VALUES (%s, %s, %s, %s) RETURNING id;
        ''', (user, title, description, False))
        task_id = cursor.fetchone()['id']
        conn.commit()
        conn.close()

        return jsonify({'message': 'Task created successfully', 'id': task_id, 'title': title, 'description': description, 'completed': False}), 201
    except Exception as e:
        return jsonify({'message': 'Error creating task', 'error': str(e)}), 500

# Route to mark a task as complete
@app.route('/tasks/<int:task_id>/complete', methods=['PUT'])
def complete_task(task_id):
    token = request.headers.get('Authorization', '').split(' ')[1]
    user = authenticate(token)
    if not user:
        return jsonify({'message': 'Unauthorized'}), 401

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE id = %s AND user_email = %s', (task_id, user))
        task = cursor.fetchone()

        if not task:
            return jsonify({'message': 'Task not found or unauthorized access'}), 404

        cursor.execute('UPDATE tasks SET completed = %s WHERE id = %s', (True, task_id))
        conn.commit()

        # Notify notification service about the task completion
        task_data = {
            "title": task['title'],
            "description": task['description']
        }

        response = requests.post(NOTIFICATION_SERVICE_URL, json=task_data)
        if response.status_code != 200:
            return jsonify({"error": "Failed to send notification"}), 500

        conn.close()
        return jsonify({'message': 'Task completed successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'Error completing task', 'error': str(e)}), 500

# Route to delete a task
@app.route('/tasks/<int:task_id>', methods=['DELETE'])
def delete_task(task_id):
    token = request.headers.get('Authorization', '').split(' ')[1]
    user = authenticate(token)
    if not user:
        return jsonify({'message': 'Unauthorized'}), 401

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM tasks WHERE id = %s AND user_email = %s', (task_id, user))
        task = cursor.fetchone()

        if not task:
            return jsonify({'message': 'Task not found or unauthorized access'}), 404

        cursor.execute('DELETE FROM tasks WHERE id = %s', (task_id,))
        conn.commit()
        conn.close()
        return jsonify({'message': 'Task deleted successfully'}), 200
    except Exception as e:
        return jsonify({'message': 'Error deleting task', 'error': str(e)}), 500

if __name__ == '__main__':
    create_table()  # Ensure that the table exists
    app.run(port=5001, debug=True)
