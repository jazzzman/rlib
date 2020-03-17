from flask import render_template, redirect, url_for, flash, request
from flask_login import current_user, login_user, login_required
from app import app, login, db
from app.forms import LoginForm
from app.models import User, Author, Publication, Journal, PubType, lab_ids,\
                        AuthorSynonym
from sqlalchemy import func, distinct


@app.route('/')
@app.route('/index', methods=['GET','POST'])
@login_required
def index():
    publications = Publication.query.order_by(Publication.year.desc())
    journals = Journal.query.all()
    years = sorted(set(Publication.query.values(Publication.year)))
    lab_authors = Author.query.filter(Author.id.in_(lab_ids))

    if request.method == 'POST':
        filters = request.get_json();
        if 'authors' in filters:
            authors = filters['authors']
            publications = publications.join(Publication.authors).\
                    filter(Author.id.in_(authors)).\
                    group_by(Publication.id).\
                    having(func.count(Publication.id) == len(authors))
        if 'pub-type' in filters:
            pub_type = [PubType(int(i)) for i in filters['pub-type']]
            publications = publications.filter(Publication.pub_type.in_(pub_type))
        if 'pub-year' in filters:
            pub_year = filters['pub-year']
            publications = publications.filter(Publication.year.in_(pub_year))
        if 'title' in filters:
            title = filters['title']
            publications = publications.filter(Publication.title.ilike(f'%{title}%'))
        if 'journal' in filters:
            journal = filters['journal']
            publications = publications.join(Publication.journal).\
                    filter(Journal.id.in_(journal)).\
                    distinct(Publication.id)
        if 'quartile' in filters:
            publications = publications.join(Publication.journal).\
                    filter(Journal.quartile.in_(filters['quartile']))
        if 'db' in filters:
            publications = publications.join(Publication.journal).\
                    filter(Journal.is_risc)

    page = request.args.get('page', 1, type=int)
    publications = publications.paginate(page, 
            app.config['PUBLICATIONS_PER_PAGE'], False)
    next_url = url_for('index', page=publications.next_num) \
        if publications.has_next else None
    prev_url = url_for('index', page=publications.prev_num) \
        if publications.has_prev else None
    max_nav_btn = min(publications.total//publications.per_page+1,page+3)+1
    nav_btns = [(url_for('index',page=i),i) for i in range(max(1,page-2),max_nav_btn)]

    if request.method == 'POST':
        print(publications.items)
        return render_template('table_publication_nav.html', 
                            publications = publications.items, curr_page = page,
                            next_url=next_url, prev_url=prev_url, nav_btns=nav_btns)
    return render_template('index.html', title='RLib', publications = publications.items,
                            curr_page=page, next_url=next_url, prev_url=prev_url, 
                            nav_btns=nav_btns,  lab_authors=lab_authors,
                            journals=journals, years=years, pub_type = PubType)

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

@app.route('/authors')
@login_required
def authors():
    authors = AuthorSynonym.query.order_by(AuthorSynonym.id.asc())
    return render_template('authors.html', title='RLib.Authors')

@app.route('/settings')
@login_required
def settings():
    return render_template('index.html', title='RLib')
