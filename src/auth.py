from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required
from models import User
from forms import LoginForm

# Blueprint for authentication routes
auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    
    if form.validate_on_submit():
        # Get user by username
        user = User.query.filter_by(username=form.username.data).first()
        
        # Password verification
        if user and user.check_password(form.password.data):
            login_user(user)
            # Redirect to dashboard after successful login
            return redirect(url_for('index'))
        
        # Invalid credentials
        flash('Invalid username or password.', 'danger')

    return render_template('login.html', form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))