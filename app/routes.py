from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, login_required
from app import app, login
from app.forms import LoginForm
from app.models import User, Publication, Journal
from sqlalchemy.ext import baked
from sqlalchemy import bindparam


@app.route('/')
@app.route('/index', methods=['GET','POST'])
@login_required
def index():

    if request.method == 'POST':
        bakery = baked.bakery()
        b_query = bakery(lambda session: session.query(Publication))
        filters = request.get_json();
        if 'authors' in filters:
            authors = filters['authors']
            b_query += lambda q: q.filter(Author.id.in_(authors))
        if 'pub-type' in filters:
            pub_type = filters['pub-type']
            b_query += lambda q: q.filter(Publication.pub_type.in_(pub_type))
        if 'pub-year' in filters:
            pub_year = filters['pub-year']
            b_query += lambda q: q.filter(Publication.year.in_(pub_year))
        if 'title' in filters:
            title = filters['title']
            b_query += lambda q: q.filter(Publication.title.ilike(title))
        if 'journal' in filters:
            journal = filters['journal']
            b_query += lambda q: q.filter(Publication.year.in_(pub_year))
        db.session.query(Publication)

    page = request.args.get('page', 1, type=int)
    publications = Publication.query.order_by(Publication.year.desc()).paginate(
            page, app.config['PUBLICATIONS_PER_PAGE'], False)
    next_url = url_for('index', page=publications.next_num) \
        if publications.has_next else None
    prev_url = url_for('index', page=publications.prev_num) \
        if publications.has_prev else None
    max_nav_btn = min(publications.total//publications.per_page+1,page+3)+1
    nav_btns = [(url_for('index',page=i),i) for i in range(max(1,page-2),max_nav_btn)]
    journals = Journal.query.all()
    years = sorted(set(Publication.query.values(Publication.year)))
    return render_template('index.html', title='RLib', publications = publications.items,
                            next_url=next_url, prev_url=prev_url, nav_btns=nav_btns,
                            journals=journals, years=years)

@app.route('/signin', methods=['GET','POST'])
def signin():
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
    return redirect(url_for('signin'))

@app.route('/add')
@login_required
def add():
    return render_template('index.html', title='RLib')

@app.route('/settings')
@login_required
def settings():
    return render_template('index.html', title='RLib')
