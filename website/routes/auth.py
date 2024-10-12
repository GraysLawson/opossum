from flask import Blueprint, redirect, url_for, session, flash
from flask_discord import Unauthorized
from flask_login import login_user, logout_user, login_required
from models import User
from utils import discord

auth_bp = Blueprint('auth', __name__)

@auth_bp.route("/login")
def login():
    return discord.create_session(scope=["identify"])

@auth_bp.route("/callback")
def callback():
    try:
        discord.callback()
        user_data = discord.fetch_user()
        user = User()
        user.id = user_data.id
        login_user(user)
        session['user_id'] = user.id
        return redirect(url_for("index"))
    except Exception as e:
        flash("An error occurred during login. Please try again.", "error")
        return redirect(url_for("index"))

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect(url_for("index"))

@auth_bp.errorhandler(Unauthorized)
def redirect_unauthorized(e):
    return redirect(url_for("auth.login"))

