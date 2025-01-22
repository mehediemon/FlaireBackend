from flask import Flask, request, jsonify
from flask_cors import CORS
import jwt
import bcrypt
import datetime
import psycopg2
from psycopg2.extras import RealDictCursor
import os

app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'your_secret_key'

# PostgreSQL database configuration

DATABASE_CONFIG = {
    'dbname': os.getenv('DB_NAME', 'user_db'),
    'user': os.getenv('DB_USER', 'test'),
    'password': os.getenv('DB_PASSWORD', '12345678'),
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': int(os.getenv('DB_PORT', 5432))
}

# Helper function to get DB connection
def get_db():
    conn = psycopg2.connect(**DATABASE_CONFIG)
    return conn

# Create users table if it doesn't exist
def init_db():
    with get_db() as conn:
        with conn.cursor() as cursor:
            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                              email TEXT PRIMARY KEY,
                              username TEXT NOT NULL,
                              password TEXT NOT NULL)''')
        conn.commit()

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    username = data.get('username')

    if not email or not password or not username:
        return jsonify({'message': 'All fields are required'}), 400

    try:
        with get_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()
                if user:
                    return jsonify({'message': 'User already exists'}), 400

                hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cursor.execute("INSERT INTO users (email, username, password) VALUES (%s, %s, %s)", 
                               (email, username, hashed_password))
                conn.commit()

        return jsonify({'message': 'User registered successfully'}), 201
    except Exception as e:
        return jsonify({'message': 'Error registering user', 'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    try:
        with get_db() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                user = cursor.fetchone()

        if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return jsonify({'message': 'Invalid credentials'}), 401

        token = jwt.encode(
            {'email': email, 'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=1)},
            app.config['SECRET_KEY'],
            algorithm='HS256'
        )
        return jsonify({'token': token}), 200
    except Exception as e:
        return jsonify({'message': 'Error during login', 'error': str(e)}), 500

if __name__ == '__main__':
    init_db()
    app.run(port=5000)
