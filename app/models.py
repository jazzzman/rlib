from app import db
from app import login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import enum
import re


author_publication = db.Table('author_publication',
        db.Column('author_id', db.Integer, db.ForeignKey('author.id', name='author_id_fk')),
        db.Column('publication_id', db.Integer, db.ForeignKey('publication.id', name='publication_id_fk')))

author_organisation = db.Table('author_organisation',
        db.Column('author_id', db.Integer, db.ForeignKey('author.id', name='author_id_fk')), 
        db.Column('organisation_id', db.Integer, db.ForeignKey('organisation.id', name='organisation_id_fk')))

lab_ids = [69, 9, 20, 10, 15, 8]


class User(UserMixin):
    id = 0
    password_hash = "pbkdf2:sha256:150000$ge61Utf3$65dd72e931cb6ee6bae9848a0c9d6ea2565b4765e7944271ef1d431d96cd235e"
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login.user_loader
def load_user(id):
    return User()

class PubType(enum.Enum):
        ConfThesis=0
        Proceedings=1
        Article=2
        Monograph=3
        Patent=4
        PhdThesis=5
        DocThesis=6
        Awards=7


class Publication(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(8128))
    volume = db.Column(db.Integer)
    issue = db.Column(db.String(250))
    pages = db.Column(db.String(255))
    year = db.Column(db.Integer)
    doi = db.Column(db.String(250))
    authors_raw = db.Column(db.String(250))
    pub_type = db.Column(db.Enum(PubType))
    journal_id = db.Column(db.Integer, db.ForeignKey('journal.id', name='journal_id_fk'))
    authors = db.relationship('Author', 
                              secondary=author_publication,
                              backref='publications')
    # journal - backref

    def from_dict(self, data):
        if 'title' in data:
            if Publication.query.filter_by(title=data['title']).first():
                print("Publication already exist", data['title'])
                return False
        if 'doi' in data and data['doi'] != '':
            if Publication.query.filter_by(doi=data['doi']).first():
                print("Publication already exist. doi:",data['doi'])
                return False
        for field in ['title', 'volume', 'issue', 'pages', 'year', 'doi', 'pub_type']:
            if field in data:
                setattr(self, field, data[field])
        if 'journal' in data:
            journal = Journal.query.filter_by(title = data['journal']).first()
            if journal is None:
                journal = Journal(title=data['journal'])
                db.session.add(journal)
            self.journal = journal
        if 'authors_raw' in data:
            self.authors_raw = data['authors_raw']
            for author_raw in data['authors_raw'].split(','):
                author_raw = author_raw.strip(" \t\n")
                r = r"\s*?([\w\\\-'`]+)\.?\s*([\w\-`]+)?\.?\s*([\w\-`]+)*"
                ms = re.match(r,author_raw)
                if ms:
                    lastname, name, patr = ms.groups()
                    try:
                        if len(lastname)<2 and patr is not None:
                            lastname, name, patr = patr, lastname, name
                        elif len(lastname)<2 and patr is None:
                            lastname, name, patr = name, lastname, patr
                        elif len(lastname)<3 and lastname.isupper():
                            lastname, name, patr = name, lastname[0], lastname[1]
                        elif len(name)==2 and name.isupper():
                            lastname, name, patr = lastname, name[0], name[1]
                    except Exception as ex:
                        print(ex,'\n',data['title'],data['authors_raw'],author_raw)
                        continue

                    isen = re.search('[A-Za-z]', lastname) is not None
                    attr_ln = 'elastname' if isen else 'lastname'
                    attr_n = 'ename' if isen else 'name'
                    attr_p = 'epatronymic' if isen else 'patronymic'
                    if isen:
                        a = Author.query.filter(Author.elastname == lastname).\
                                         filter(Author.ename == name)
                    else:
                        a = Author.query.filter(Author.lastname == lastname).\
                                         filter(Author.name == name)

                    if patr is not None:
                        if isen:
                            a=a.filter(Author.epatronymic == patr)
                        else:
                            a=a.filter(Author.patronymic == patr)
                    a = a.first()
                    if a is None:
                        a = Author()
                        setattr(a, attr_ln, lastname)
                        setattr(a, attr_n, name)
                        setattr(a, attr_p, patr)
                        db.session.add(a)
                    self.authors.append(a.main or a)
                else:
                    print(author_raw,'doesnt match to pattern')
        return True

    def to_dict(self):
        data={}
        for field in ['title', 'volume', 'issue', 'pages', 'year', 'doi', 'pub_type']:
            data[field] = getattr(self,field)
        data['authors'] = ', '.join([str(a) for a in self.authors])
        data['journal'] = self.journal.title if self.journal is not None else ''
        return(data)


    def to_gost(self):
        isen = len(re.findall('[a-zA-z]', self.title)) > .6*len(self.title)
        attr = []
        attr.append(self.journal.title if self.journal is not None else None)
        attr.append(self.year)
        attr.append(self.volume)
        attr.append(self.issue)
        attr.append("С. " + self.pages if self.pages is not None else None)
        attr = [str(a) for a in attr if a is not None]
        try:
            output =(
                    f'{", ".join([a.to_gost(not isen) for a in self.authors])} '
                    f'{self.title} //'
                    f'{". - ".join(attr)}'
                    )
        except:
            print(self.id, self.title, end=' ') 
            output = 'None'
        return output

    def __repr__(self):
        return f'{self.authors_raw} {self.title}'


class Journal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(8128))
    quartile_SJR = db.Column(db.Integer)
    quartile_JCR = db.Column(db.Integer)
    is_wos = db.Column(db.Boolean)
    is_scopus = db.Column(db.Boolean)
    is_risc = db.Column(db.Boolean)
    publications = db.relationship('Publication', backref='journal', lazy='dynamic')

    def publication_count(self):
        return self.publications.count()

    def from_dict(self, data):
        if 'title' in data and Journal.query.filter_by(title=data['title']).first():
            print('Journal already exist:',data['title'])
            return False

        for field in ['title', 'quartile_JCR', 'quartile_SJR', 'is_risc', 'is_scopus', 'is_wos']:
            if field in data:
                setattr(self, field, data[field])
        if 'quartile' in data:
            self.quartile_JCR = self.quartile_SJR = data['quartile']
        return True



    def __repr__(self):
        return f'{self.title}'


class Author(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    patronymic = db.Column(db.String(255))
    lastname = db.Column(db.String(255))
    ename = db.Column(db.String(255))
    epatronymic = db.Column(db.String(255))
    elastname = db.Column(db.String(255))
    synonym_id = db.Column(db.Integer, 
            db.ForeignKey('author.id', name='synonym_id_fk'))
    synonym = db.relationship("Author", 
            backref=db.backref('main', remote_side=[id]))
    # publications - backref
    # organisations - backref
    # main - backref

    def get_all_publications(self):
        author = self.main or self
        return author.publications + [p for s in author.synonym for p in s.publications]

    def to_dict(self):
        data = {
                "id": self.id,
                "name": self.name,
                "lastname": self.lastname,
                "patronymic": self.patronymic,
                "ename": self.ename,
                "elastname": self.elastname,
                "epatronymic": self.epatronymic,
                "main_id": self.main.id if self.main else -1,
                "synonym": [s.id for s in self.synonym],
            }
        return data

    def to_gost(self, rus=None):
        ruath = self.lastname not in ['', None]
        if rus is None or (rus ^ ruath):
            return self.to_gost(ruath)
        elif rus and ruath:
            return (
                    f'{self.lastname} '
                    f'{self.name[0]}.'
                    f'{self.patronymic[0]+"." if self.patronymic is not None else ""}'
                    )
        elif not rus and not ruath:
            return (
                    f'{self.elastname} '
                    f'{self.ename[0]}.'
                    f'{self.epatronymic[0]+"." if self.epatronymic is not None else ""}'
                    )
        else:
            return 


    def __repr__(self):
        return self.to_gost() 


class Organisation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    authors = db.relationship('Author',
            secondary=author_organisation,
            backref='organisations')

    def __repr__(self):
        return self.title


