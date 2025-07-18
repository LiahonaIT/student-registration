import os
from flask import Flask, request, flash, redirect, url_for
from werkzeug.exceptions import RequestEntityTooLarge

from config import Config
from extensions import db, mail
from auth import auth_bp, login_manager
from registration import registration_bp
from admin import admin_bp

# ——— 1) Create the Flask app ———
app = Flask(__name__)
app.config.from_object(Config)

# ——— 2) Bind extensions ———
db.init_app(app)
mail.init_app(app)

# ——— 3) Init Flask-Login (only once!) ———
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'warning'

# ——— 4) Error handler for too-big uploads ———
@app.errorhandler(RequestEntityTooLarge)
def handle_file_too_large(e):
    flash("That file was too large (max 2 MB).", "danger")
    return redirect(request.url), 413

# ——— 5) CLI helper ———
@app.cli.command("initdb")
def initdb():
    db.create_all()
    print("✅ Initialized the database.")

# ——— 6) Register blueprints ———
app.register_blueprint(auth_bp)
app.register_blueprint(registration_bp)
app.register_blueprint(admin_bp)

if __name__ == "__main__":
    app.run(debug=True)
