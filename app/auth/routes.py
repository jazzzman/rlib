from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_user
from app import app, login 
from app.auth.forms import LoginForm
from app.models import User
from app.auth import bp


@bp.route('/signin', methods=['GET','POST'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User()
        if not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('auth.signin'))
        login_user(user, remember=False)
        return redirect(url_for('main.index'))
    return render_template('login.html', title='Sign In', form=form)


@login.unauthorized_handler
def unauthorized():
    return redirect(url_for('auth.signin'))



