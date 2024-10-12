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
from utils import get_redis_connection
from models import User

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

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User(id=user_id)

# Import and register blueprints
from routes.auth import auth_bp
from routes.config import config_bp
from routes.logs import logs_bp

app.register_blueprint(auth_bp)
app.register_blueprint(config_bp)
app.register_blueprint(logs_bp)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
