from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required
import os
from utils import get_redis_connection
import json
import requests

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

@config_bp.route('/config/roles', methods=['GET', 'POST'])
@login_required
def config_roles():
    if request.method == 'POST':
        selected_roles = request.form.getlist('roles')
        guild_id = request.form.get('guild_id')
        redis_client = get_redis_connection()
        roles = {role_id: role_name for role_id, role_name in zip(request.form.getlist('role_ids'), request.form.getlist('role_names')) if role_id in selected_roles}
        redis_client.set(f'role_assignment_roles:{guild_id}', json.dumps(roles))
        flash('Role configuration updated successfully', 'success')
        return redirect(url_for('config.config_roles'))
    else:
        redis_client = get_redis_connection()
        guild_ids_json = redis_client.get('bot_guild_ids')
        guild_ids = json.loads(guild_ids_json) if guild_ids_json else []

        selected_guild_id = request.args.get('guild_id', guild_ids[0] if guild_ids else None)

        bot_token = os.getenv('DISCORD_TOKEN')
        headers = {'Authorization': f'Bot {bot_token}'}

        guilds = []
        for guild_id in guild_ids:
            response = requests.get(f'https://discord.com/api/v10/guilds/{guild_id}', headers=headers)
            if response.status_code == 200:
                guild_data = response.json()
                guilds.append({'id': guild_id, 'name': guild_data['name']})

        if selected_guild_id:
            response = requests.get(f'https://discord.com/api/v10/guilds/{selected_guild_id}/roles', headers=headers)
            all_roles = response.json() if response.status_code == 200 else []

            selected_roles_json = redis_client.get(f'role_assignment_roles:{selected_guild_id}')
            selected_roles = json.loads(selected_roles_json) if selected_roles_json else {}
        else:
            all_roles = []
            selected_roles = {}

        return render_template('config_roles.html', guilds=guilds, selected_guild_id=selected_guild_id, all_roles=all_roles, selected_roles=selected_roles)
