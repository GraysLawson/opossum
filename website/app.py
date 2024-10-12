from flask import Flask, render_template, request, redirect, url_for, session, flash, Response
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from werkzeug.middleware.proxy_fix import ProxyFix
import os
import redis
import json
from datetime import datetime
from functools import wraps
import time
from models import User
from config import discord, init_discord, DISCORD_TOKEN
import requests

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
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

init_discord(app)

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

@app.route('/config/roles', methods=['GET', 'POST'])
@login_required
def config_roles():
    if request.method == 'POST':
        selected_roles = request.form.getlist('roles')
        redis_client = redis.Redis.from_url(REDIS_URL)
        roles = {role_id: role_name for role_id, role_name in zip(request.form.getlist('role_ids'), request.form.getlist('role_names')) if role_id in selected_roles}
        redis_client.set('role_assignment_roles', json.dumps(roles))
        flash('Role configuration updated successfully', 'success')
        return redirect(url_for('config_roles'))
    else:
        # Fetch roles from Discord API
        guild_id = os.getenv('DISCORD_GUILD_ID')
        headers = {'Authorization': f'Bot {DISCORD_TOKEN}'}
        response = requests.get(f'https://discord.com/api/v10/guilds/{guild_id}/roles', headers=headers)
        all_roles = response.json()

        # Fetch currently selected roles from Redis
        redis_client = redis.Redis.from_url(REDIS_URL)
        selected_roles_json = redis_client.get('role_assignment_roles')
        selected_roles = json.loads(selected_roles_json) if selected_roles_json else {}

        return render_template('config_roles.html', all_roles=all_roles, selected_roles=selected_roles)

# Add this near the top of your file, with other imports
REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379')

if __name__ == "__main__":
    app.run(debug=True)
