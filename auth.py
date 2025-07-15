# auth.py

from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from werkzeug.security import check_password_hash
from forms import LoginForm

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

# reuse the same LoginManager instance
login_manager = LoginManager()

class AdminUser(UserMixin):
    def __init__(self):
        self.id = 'admin'

@login_manager.user_loader
def load_user(user_id):
    return AdminUser() if user_id == 'admin' else None

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('auth.login', next=request.path))

@auth_bp.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    form = LoginForm()
    if form.validate_on_submit():
        u, p = form.username.data, form.password.data
        cfg = current_app.config
        if u == cfg['ADMIN_USERNAME'] and check_password_hash(cfg['ADMIN_PASSWORD_HASH'], p):
            user = AdminUser()
            login_user(user)
            return redirect(request.args.get('next') or url_for('admin.dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out', 'info')
    return redirect(url_for('auth.login'))
