from flask import Blueprint, render_template, Response
from flask_login import login_required
from utils import get_redis_connection
import json
import time

logs_bp = Blueprint('logs', __name__)

@logs_bp.route('/logs')
@login_required
def logs():
    try:
        redis_client = get_redis_connection()
        logs_data = redis_client.lrange('bot_logs', 0, 99)  # Get the latest 100 logs
        logs = [json.loads(log) for log in logs_data]
        return render_template('logs.html', logs=logs)
    except Exception as e:
        return render_template('logs.html', logs=[], error="An error occurred while fetching logs.")

@logs_bp.route('/stream-logs')
@login_required
def stream_logs():
    def generate():
        redis_client = get_redis_connection()
        last_id = 0
        while True:
            logs = redis_client.lrange('bot_logs', 0, -1)
            if logs:
                for log in reversed(logs):
                    log_data = json.loads(log)
                    if int(log_data['timestamp']) > last_id:
                        last_id = int(log_data['timestamp'])
                        yield f"data: {json.dumps(log_data)}\n\n"
            time.sleep(1)

    return Response(generate(), mimetype='text/event-stream')

