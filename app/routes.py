from flask import render_template, redirect, url_for, flash
from flask_login import current_user, login_user, login_required
from app import app, login
from app.forms import LoginForm
from app.models import User, Publication

@app.route('/')
@app.route('/index')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    publications = Publication.query.order_by(Publication.year.desc()).paginate(
            page, app.config['PUBLICATIONS_PER_PAGE'], False)
    next_url = url_for('index', page=publications.next_num) \
        if posts.has_next else None
    prev_url = url_for('index', page=publications.prev_num) \
        if posts.has_prev else None
    return render_template('index.html', title='RLib', publications = publications.items,
                            next_url=ndexy_url, prev_url=prev_url)

@app.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User()
        if not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=False)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@login.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))

@app.route('/add')
@login_required
def add():
    return render_template('index.html', title='RLib')

@app.route('/settings')
@login_required
def settings():
    return render_template('index.html', title='RLib')
