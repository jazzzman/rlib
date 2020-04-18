import clipboard
import tempfile
import json
from flask import (render_template, redirect, url_for, flash, 
        request, jsonify, session, abort, send_file, make_response)
from flask_login import current_user, login_user, login_required
from app import app, login, db, bootstrap
from app.forms import LoginForm
from app.models import (User, Author, Publication, Journal, PubType, 
        lab_ids, pub_columns, ExtPubColumn)
from sqlalchemy import func, distinct, or_
from jinja2 import Template, Environment, PackageLoader, select_autoescape


@app.route('/')
@app.route('/index', methods=['GET','POST'])
@login_required
def index():
    publications = Publication.query.order_by(Publication.year.desc())
    journals = Journal.query.order_by(Journal.title.asc()).all()
    years = sorted(set(Publication.query.values(Publication.year)),
                reverse=True)
    lab_authors = Author.query.filter(Author.id.in_(lab_ids))
    pub_columns.update({k[0]:False for k in db.session.query(ExtPubColumn.name).distinct()} )
    page=1
    if request.method == 'POST':
        filters = request.get_json() or request.form.to_dict()
        publications = apply_filters(publications ,filters)
        page = int(filters.get('page',1))
        if 'pub_columns' in filters:
            pub_cols = filters['pub_columns']
        else:
            pub_cols=pub_columns

    print(publications.statement)
    publications = publications.distinct().paginate(page, 
            app.config['PUBLICATIONS_PER_PAGE'], False)
    print(publications.query.statement)
    next_url = url_for('index', page=publications.next_num) \
        if publications.has_next else None
    prev_url = url_for('index', page=publications.prev_num) \
        if publications.has_prev else None
    max_nav_btn = min(publications.total//publications.per_page+1,page+2)+1
    nav_btns = [(url_for('index',page=i),i) for i in range(max(1,page-2),max_nav_btn)]
    pages_info = {'total':publications.total} 
    pages_info['from'] = (page-1)*app.config['PUBLICATIONS_PER_PAGE']+1
    pages_info['to'] = min(pages_info['total'],page*app.config['PUBLICATIONS_PER_PAGE'])

    if request.method == 'POST' and 'redirect' not in filters:
        return render_template('table_publication_nav.html', 
                            publications = publications.items, curr_page = page,
                            next_url=next_url, prev_url=prev_url, nav_btns=nav_btns,
                            pages_info=pages_info, pub_columns=pub_cols)
    return render_template('index.html', title='RLib', 
                            publications = publications.items, curr_page=page, 
                            next_url=next_url, prev_url=prev_url, nav_btns=nav_btns, 
                            lab_authors=lab_authors,
                            journals=journals, years=years, pub_type = PubType,
                            pages_info=pages_info, pub_columns=pub_columns)


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
    required = {
            'authors_raw':'Empty authors', 
            'title':'Empty title',
            'journal':'Empty journal/book/issue',
            'year':'Year cannot be Null',
            'pub_type':'Select publication type'
        }
    if request.method == 'POST':
        # TODO implement through api
        data = request.get_json() or {}
        empty_required={k:v for k,v in required.items() if k in data and (data[k]=='' or data[k]==None)}
        if ('title' not in empty_required and
            Publication.query.filter_by(title=data['title']).count()!=0):
            empty_required['title']='Publication already exists'
        if len(empty_required)>0:
            return abort(make_response(jsonify(empty_required), 400))

        pb = Publication()
        resp = pb.from_dict(data)
        db.session.commit()
        if resp['reject']:
            return jsonify({'reject':resp['message']})
        elif resp['warnings'] != '':
            return jsonify({'warnings':resp['warnings']})
        return '200'
    return render_template('add.html', title='RLib', pub_type = PubType)


@app.route('/authors', methods=['GET','POST'])
@login_required
def authors():
    if request.method == 'POST':
        # TODO implement through api
        rdata = {}
        data = request.get_json() or {}
        if 'id' not in data:
            return
        asyn = Author.query.get_or_404(data['id'])
        if 'main_id' in data:
            asyn.set_main(Author.query.get(data['main_id']))
            rdata = asyn.to_dict()
            rdata["main_repr"] = str(asyn.main) if asyn.main else ""
        for field in [k for k in data.keys() if k not in ['id','main_id']]:
            setattr(asyn, field, data[field] if data[field] != '' else None)
        db.session.commit()
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


@app.route('/output', methods=['GET','POST'])
@login_required
def output():
    if request.method == 'POST':
        data = request.get_json()
        publications = Publication.query.order_by(Publication.year.desc())
        publications = apply_filters(publications, 
                data.get('filters',{})).\
                all()
        plain = '\n'.join([p.to_gost() for p in publications])
        if data['type'] == 'clipboard':
            clipboard.copy(plain)
            return '200' 
        elif data['type'] == 'csv':
            return jsonify([plain, 'publications.txt'])
    else:
        abort(404)


@app.route('/update', methods=['GET','POST'])
@login_required
def update():
    if request.method == 'POST':
        data = request.get_json()
        publication = Publication.query.get_or_404(data['id'])
        for field in [f for f in data.keys() if f not in ['id','pub_type']]:
            setattr(publication,field,data[field])
        if 'pub_type' in data:
            setattr(publication,'pub_type',PubType[data['pub_type']])

        db.session.commit()
        return '200' 
    else:
        abort(404)


@app.route('/addcolumn', methods=['GET','POST'])
@login_required
def addcolumn():
    if request.method == 'POST':
        data = request.get_data().decode('utf8')
        if data in [*db.session.query(ExtPubColumn.name).distinct(), *pub_columns.keys()]:
            return abort(404)
        for p in Publication.query.all():
            p.add_fields.append(ExtPubColumn(name=data))
        db.session.commit()

        return ''' 
                    <div class="form-check">
                        <input type="checkbox" class="form-check-input" value="{{key}}" id="colsel-{{key}}" autocomplete="off" checked>
                        <label class="form-check-label" for="colsel-{{key}}">{{key}}</label>
                    </div>
                '''.replace('{{key}}',data)
    return abort(400)


@app.route('/deletepubs', methods=['GET','POST'])
@login_required
def deletepubs():
    if request.method == 'POST':
        data = request.get_json() or []
        dicts = [p.to_gost()
                for p in Publication.query.filter(Publication.id.in_(data))]
        nt = '\n\t'
        app.logger.info(f'DELETE PUBLICATIONS{nt}{nt.join(dicts)}')
        for d in data:
            Publication.query.filter(Publication.id==d).delete()
        db.session.commit()
        return '200'
    return abort(400)


def apply_filters(publications, filters):
    print(filters)
    if 'authors' in filters:
        authors = filters['authors']
        publications = publications.join(Publication.authors).\
                filter(Author.id.in_(authors))#.\
        if filters.get('ath_intersection', False):
            publications = publications.group_by(Publication.id).\
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
        db = []
        if 'wos' in filters['db']:
            db.append(Journal.is_wos)
        if 'scopus' in filters['db']:
            db.append(Journal.is_scopus)
        if 'risc' in filters['db']:
            db.append(Journal.is_risc)
        publications = publications.join(Publication.journal).\
                filter(or_(*db))
    return publications

@app.template_filter('jsonPresOrd')
def json_preserve_order(input):
    return json.dumps(input)


@app.template_filter('to_gost')
def auth_gost(input, rus=False):
    return [a.to_gost(rus) for a in input]
