from flask import Flask, request, jsonify
import requests
import redis
import json
import threading
import time
import os

app = Flask(__name__)

# Telegram Bot API configuration
TELEGRAM_BOT_TOKEN = "721xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxSzSGs"
TELEGRAM_CHAT_ID = "-1xxxxxxxxxxxx18"  # Replace with the chat ID or group ID

# Setup Redis connection
redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')  # Replace with your Redis URL if hosted externally
r = redis.Redis.from_url(redis_url)

# Redis Queue Name
QUEUE_NAME = "notification_queue"

def send_telegram_notification(task_title, task_description):
    """
    Function to send a Telegram notification to the group.
    This function is executed by the background thread.
    """
    try:
        message = f"🎉 Task Completed!\n\nTitle: {task_title}\nDescription: {task_description}"

        # Send message to Telegram bot
        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
            json={"chat_id": TELEGRAM_CHAT_ID, "text": message}
        )

        if response.status_code == 200:
            print("Notification sent successfully!")
        else:
            print("Failed to send notification")
    except Exception as e:
        print(f"Error sending notification: {str(e)}")

def process_notification_queue():
    """
    Function to continuously process tasks from the Redis queue.
    This runs in a background thread.
    """
    while True:
        # Get the next notification task from the Redis queue (blocking)
        task = r.blpop(QUEUE_NAME, timeout=0)  # blocking pop from queue
        if task:
            task_data = json.loads(task[1])
            task_title = task_data.get('title')
            task_description = task_data.get('description', 'No description provided.')

            # Send the notification
            send_telegram_notification(task_title, task_description)
        time.sleep(1)  # Sleep for a short time before checking the queue again

@app.route('/notify', methods=['POST'])
def send_notification():
    try:
        data = request.json
        task_title = data.get('title')
        task_description = data.get('description', 'No description provided.')

        # Validate inputs
        if not task_title:
            return jsonify({"error": "Title is required"}), 400

        # Add the task to the Redis queue
        task_data = {
            "title": task_title,
            "description": task_description
        }

        # Push the task to the Redis queue
        r.rpush(QUEUE_NAME, json.dumps(task_data))

        return jsonify({"message": "Notification request has been queued for processing!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Start the background thread to process the queue
    threading.Thread(target=process_notification_queue, daemon=True).start()
    app.run(host='0.0.0.0', port=5002, debug=True)
