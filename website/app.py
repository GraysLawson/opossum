from flask import Flask, render_template, request, redirect, url_for
import os
import redis
import json

app = Flask(__name__)

REDIS_URL = os.getenv('REDIS_URL')

if not REDIS_URL:
    app.logger.error("REDIS_URL is not set")
    raise ValueError("REDIS_URL environment variable is not set")

def get_redis_connection():
    return redis.Redis.from_url(REDIS_URL)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/logs')
def logs():
    try:
        redis_client = get_redis_connection()
        logs_data = redis_client.lrange('bot_logs', 0, 99)  # Get the latest 100 logs
        logs = [json.loads(log) for log in logs_data]
        app.logger.info(f"Retrieved {len(logs)} logs from Redis")
        return render_template('logs.html', logs=logs)
    except redis.exceptions.ConnectionError as e:
        app.logger.error(f"Redis connection error: {str(e)}")
        return render_template('logs.html', logs=[], error="Failed to connect to Redis server.")
    except json.JSONDecodeError as e:
        app.logger.error(f"JSON decode error: {str(e)}")
        return render_template('logs.html', logs=[], error="Error parsing log data.")
    except Exception as e:
        app.logger.error(f"An unexpected error occurred while fetching logs: {str(e)}")
        return render_template('logs.html', logs=[], error="An unexpected error occurred while fetching logs.")

@app.route('/config', methods=['GET', 'POST'])
def config():
    if request.method == 'POST':
        discord_token = request.form.get('discord_token')
        openai_api_key = request.form.get('openai_api_key')
        active_channels = request.form.getlist('active_channels')
        openai_model = request.form.get('openai_model')

        os.environ['DISCORD_TOKEN'] = discord_token
        os.environ['OPENAI_API_KEY'] = openai_api_key
        os.environ['ACTIVE_CHANNELS'] = ','.join(active_channels) if active_channels else ''
        os.environ['OPENAI_MODEL'] = openai_model

        return redirect(url_for('config'))
    else:
        discord_token = os.getenv('DISCORD_TOKEN', '')
        openai_api_key = os.getenv('OPENAI_API_KEY', '')
        active_channels = os.getenv('ACTIVE_CHANNELS', '').split(',')
        openai_model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        
        redis_client = get_redis_connection()
        channels_json = redis_client.get('discord_channels')
        channels = json.loads(channels_json) if channels_json else []

        available_models = ['gpt-4o-mini', 'gpt-4o', 'chatgpt-4o-latest']
        
        return render_template('config.html', 
                               discord_token=discord_token, 
                               openai_api_key=openai_api_key, 
                               active_channels=active_channels,
                               openai_model=openai_model,
                               available_models=available_models,
                               channels=channels)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
