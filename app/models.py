from app import db
from app import login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import enum


author_publication = db.Table('author_publication',
        db.Column('author_id', db.Integer, db.ForeignKey('author.id', name='author_id_fk')),
        db.Column('publication_id', db.Integer, db.ForeignKey('publication.id', name='publication_id_fk')))

author_organisation = db.Table('author_organisation',
        db.Column('author_id', db.Integer, db.ForeignKey('author.id', name='author_id_fk')), 
        db.Column('organisation_id', db.Integer, db.ForeignKey('organisation.id', name='organisation_id_fk')))

lab_ids = [12, 9, 20, 10, 15, 8]


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
    #journal - backref

    def __repr__(self):
        return f'{self.authors_raw} {self.title}'


class Journal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(8128))
    quartile = db.Column(db.Integer)
    is_wos = db.Column(db.Boolean)
    is_scopus = db.Column(db.Boolean)
    is_risc = db.Column(db.Boolean)
    publications = db.relationship('Publication', backref='journal', lazy='dynamic')

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
    synonym = db.relationship("AuthorSynonym", backref="main")
    # publications - backref
    # organisations - backref

    def __repr__(self):
        return f'{self.lastname} {self.name[0] if self.name is not None else "X"}.'

class Organisation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    authors = db.relationship('Author',
            secondary=author_organisation,
            backref='organisations')

    def __repr__(self):
        return self.title

class AuthorSynonym(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    main_id = db.Column(db.Integer, db.ForeignKey("author.id", name='main_id_fk'))
    lastname = db.Column(db.String(255))
    name = db.Column(db.String(255)) 
    patronymic = db.Column(db.String(255))
    # main - backref

    def to_dict(self):
        data = {
            'id': self.id,
            'main_id': self.main_id,
            'lastname': self.lastname,
            'name': self.name,
            'patronymic': self.patronymic,
            'repr': str(self.main)
        }
        return data

    def __repr__(self):
        return f'{self.lastname} {self.name}'
