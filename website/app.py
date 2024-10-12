from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
from flask_discord import DiscordOAuth2Session, requires_authorization, Unauthorized
import os
import redis
import json
from datetime import datetime
from functools import wraps
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user
from werkzeug.middleware.proxy_fix import ProxyFix
import time

app = Flask(__name__)

# Use the SECRET_KEY from environment variables
secret_key = os.getenv('SECRET_KEY')
if not secret_key:
    app.logger.error("SECRET_KEY is not set")
    raise ValueError("SECRET_KEY environment variable is not set")

app.secret_key = secret_key
app.config["DISCORD_CLIENT_ID"] = os.getenv("DISCORD_CLIENT_ID")
app.config["DISCORD_CLIENT_SECRET"] = os.getenv("DISCORD_CLIENT_SECRET")
app.config["DISCORD_REDIRECT_URI"] = os.getenv("DISCORD_REDIRECT_URI")

# Determine environment
ENV = os.getenv("FLASK_ENV", "production")

if ENV == "development":
    # Allow insecure transport for development
    app.config['OAUTHLIB_INSECURE_TRANSPORT'] = 1
else:
    # Enforce HTTPS in production
    app.config['OAUTHLIB_INSECURE_TRANSPORT'] = 0
    # Apply ProxyFix to handle reverse proxy headers
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

discord = DiscordOAuth2Session(app)

REDIS_URL = os.getenv('REDIS_URL')

if not REDIS_URL:
    app.logger.error("REDIS_URL is not set")
    raise ValueError("REDIS_URL environment variable is not set")

def get_redis_connection():
    return redis.Redis.from_url(REDIS_URL)

def login_required_decorator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not discord.authorized:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/login")
def login():
    return discord.create_session(scope=["identify"])

@app.route("/callback")
def callback():
    try:
        discord.callback()
        user_data = discord.fetch_user()
        user = User()
        user.id = user_data.id
        login_user(user)
        session['user_id'] = user.id  # Store user_id in session
        return redirect(url_for("index"))
    except Exception as e:
        app.logger.error("Error in callback:", exc_info=True)
        flash("An error occurred during login. Please try again.", "error")
        return redirect(url_for("index"))

@app.route("/logout")
@login_required_decorator
def logout():
    logout_user()
    session.clear()  # Clear the entire session
    return redirect(url_for("index"))

@app.route('/logs')
@login_required_decorator
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

@app.route('/config')
@login_required_decorator
def config():
    return render_template('config.html')

@app.route('/config/tokens', methods=['GET', 'POST'])
@login_required_decorator
def config_tokens():
    if request.method == 'POST':
        discord_token = request.form.get('discord_token')
        openai_api_key = request.form.get('openai_api_key')
        os.environ['DISCORD_TOKEN'] = discord_token
        os.environ['OPENAI_API_KEY'] = openai_api_key
        flash('Tokens and API keys updated successfully', 'success')
        return redirect(url_for('config_tokens'))
    else:
        discord_token = os.getenv('DISCORD_TOKEN', '')
        openai_api_key = os.getenv('OPENAI_API_KEY', '')
        return render_template('config_tokens.html', discord_token=discord_token, openai_api_key=openai_api_key)

@app.route('/config/channels', methods=['GET', 'POST'])
@login_required_decorator
def config_channels():
    if request.method == 'POST':
        active_channels = request.form.getlist('active_channels')
        os.environ['ACTIVE_CHANNELS'] = ','.join(active_channels) if active_channels else ''
        flash('Active channels updated successfully', 'success')
        return redirect(url_for('config_channels'))
    else:
        active_channels = os.getenv('ACTIVE_CHANNELS', '').split(',')
        redis_client = get_redis_connection()
        channels_json = redis_client.get('discord_channels')
        channels = json.loads(channels_json) if channels_json else []
        return render_template('config_channels.html', active_channels=active_channels, channels=channels)

@app.route('/config/model', methods=['GET', 'POST'])
@login_required_decorator
def config_model():
    if request.method == 'POST':
        openai_model = request.form.get('openai_model')
        os.environ['OPENAI_MODEL'] = openai_model
        flash('OpenAI model updated successfully', 'success')
        return redirect(url_for('config_model'))
    else:
        openai_model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        available_models = ['gpt-4o-mini', 'gpt-4o', 'chatgpt-4o-latest', 'gpt-4-vision-preview']
        return render_template('config_model.html', openai_model=openai_model, available_models=available_models)

@app.route('/stream-logs')
@login_required_decorator
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

@app.errorhandler(Unauthorized)
def redirect_unauthorized(e):
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(UserMixin):
    def __init__(self, id=None):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    user = User(user_id)
    return user
