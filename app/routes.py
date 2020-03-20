from flask import (render_template, redirect, url_for, flash, 
        request, jsonify, session)
from flask_login import current_user, login_user, login_required
from app import app, login, db
from app.forms import LoginForm
from app.models import User, Author, Publication, Journal, PubType, lab_ids
from sqlalchemy import func, distinct, or_

@app.route('/')
@app.route('/index', methods=['GET','POST'])
@login_required
def index():
    publications = Publication.query.order_by(Publication.year.desc())
    journals = Journal.query.order_by(Journal.title.asc()).all()
    years = sorted(set(Publication.query.values(Publication.year)),
                reverse=True)
    lab_authors = Author.query.filter(Author.id.in_(lab_ids))
    page=1
    if request.method == 'POST':
        filters = request.get_json()
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
                    filter(or_(Journal.quartile_SJR.in_(filters['quartile']),
                               Journal.quartile_JCR.in_(filters['quartile'])))
        if 'db' in filters:
            publications = publications.join(Publication.journal).\
                    filter(Journal.is_risc)
        page = int(filters.get('page',1))

    # page = request.args.get('page', 1, type=int)
    publications = publications.paginate(page, 
            app.config['PUBLICATIONS_PER_PAGE'], False)
    next_url = url_for('index', page=publications.next_num) \
        if publications.has_next else None
    prev_url = url_for('index', page=publications.prev_num) \
        if publications.has_prev else None
    max_nav_btn = min(publications.total//publications.per_page+1,page+3)+1
    nav_btns = [(url_for('index',page=i),i) for i in range(max(1,page-2),max_nav_btn)]

    if request.method == 'POST':
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


@app.route('/add', methods=['GET','POST'])
@login_required
def add():
    if request.method == 'POST':
        # TODO implement through api
        data = request.get_json() or {}
        pb = Publication()
        pb.from_dict(data)
        db.session.commit()
        return res
    return render_template('add.html', title='RLib', pub_type = PubType)


@app.route('/authors', methods=['GET','POST'])
@login_required
def authors():
    if request.method == 'POST':
        # TODO implement through api
        data = request.get_json() or {}
        print(data)
        if 'id' not in data:
            return
        asyn = Author.query.get_or_404(data['id'])
        asyn.main = Author.query.get(data['main_id'])
        db.session.commit()
        rdata = asyn.to_dict()
        rdata["main_repr"] = str(asyn.main) if asyn.main else ""
        return jsonify(rdata)
    authors = Author.query.order_by(Author.lastname.asc()).all()
    return render_template('authors.html', title='RLib.Authors',
            authors=authors)


@app.route('/journals', methods=['GET','POST'])
@login_required
def journals():
    if request.method == 'POST':
        # TODO implement through api
        data = request.get_json() or {}
        try:
            j = Journal.query.get(data["id"])
            setattr(j, data['field'], data['value'])
            db.session.commit()
            return str(True)
        except Exception as ex:
            return ex
    journals = Journal.query.all()
    return render_template('journals.html', title = 'RLib.Journals',
            journals=journals)


@app.route('/settings')
@login_required
def settings():
    return render_template('index.html', title='RLib')
