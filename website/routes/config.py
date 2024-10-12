from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
import os
from utils import get_redis_connection
import json

config_bp = Blueprint('config', __name__)

@config_bp.route('/config')
@login_required
def config():
    return render_template('config.html')

@config_bp.route('/config/tokens', methods=['GET', 'POST'])
@login_required
def config_tokens():
    if request.method == 'POST':
        discord_token = request.form.get('discord_token')
        openai_api_key = request.form.get('openai_api_key')
        os.environ['DISCORD_TOKEN'] = discord_token
        os.environ['OPENAI_API_KEY'] = openai_api_key
        flash('Tokens and API keys updated successfully', 'success')
        return redirect(url_for('config.config_tokens'))
    else:
        discord_token = os.getenv('DISCORD_TOKEN', '')
        openai_api_key = os.getenv('OPENAI_API_KEY', '')
        return render_template('config_tokens.html', discord_token=discord_token, openai_api_key=openai_api_key)

@config_bp.route('/config/channels', methods=['GET', 'POST'])
@login_required
def config_channels():
    if request.method == 'POST':
        active_channels = request.form.getlist('active_channels')
        os.environ['ACTIVE_CHANNELS'] = ','.join(active_channels) if active_channels else ''
        flash('Active channels updated successfully', 'success')
        return redirect(url_for('config.config_channels'))
    else:
        active_channels = os.getenv('ACTIVE_CHANNELS', '').split(',')
        redis_client = get_redis_connection()
        channels_json = redis_client.get('discord_channels')
        channels = json.loads(channels_json) if channels_json else []
        return render_template('config_channels.html', active_channels=active_channels, channels=channels)

@config_bp.route('/config/model', methods=['GET', 'POST'])
@login_required
def config_model():
    if request.method == 'POST':
        openai_model = request.form.get('openai_model')
        os.environ['OPENAI_MODEL'] = openai_model
        flash('OpenAI model updated successfully', 'success')
        return redirect(url_for('config.config_model'))
    else:
        openai_model = os.getenv('OPENAI_MODEL', 'gpt-4o-mini')
        available_models = ['gpt-4o-mini', 'gpt-4o', 'chatgpt-4o-latest', 'gpt-4-vision-preview']
        return render_template('config_model.html', openai_model=openai_model, available_models=available_models)

