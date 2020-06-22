from app import db, app
from app import login
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import enum
import re
from sqlalchemy.sql.expression import func
from sqlalchemy import update, insert, delete
from difflib import SequenceMatcher as SM


author_publication = db.Table('author_publication',
        db.Column('author_id', db.Integer, 
            db.ForeignKey('author.id', name='author_id_fk', ondelete='CASCADE')),
        db.Column('main_id', db.Integer ),
        db.Column('publication_id', db.Integer, 
            db.ForeignKey('publication.id', name='publication_id_fk', ondelete='CASCADE')),
        db.Column('order', db.Integer))



author_organisation = db.Table('author_organisation',
        db.Column('author_id', db.Integer, db.ForeignKey('author.id', name='author_id_fk')), 
        db.Column('organisation_id', db.Integer, db.ForeignKey('organisation.id', name='organisation_id_fk')))

lab_ids = [15, 20, 3, 8, 41, 33, 126, 120, 95, 201, 360,
            42, 254, 180, 238, 444, 85, ]

pub_columns = {
        'id': True, 
        'authors': True,
        'title': True,
        'journal': True,
        'year': True,
        'volume': False,
        'issue': False,
        'pages': False,
        'doi': False,
        'quartile_JCR': False,
        'quartile_SJR': False,
        'pub_type': True,
        } 

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
                              backref='publications',
                              order_by=author_publication.c.order,
                              viewonly=True)
    add_fields = db.relationship('ExtPubColumn', backref='publication', 
            lazy='dynamic', cascade = "all, delete, delete-orphan")
    # journal - backref
    
    def isen(self):
        return len(re.findall('[a-zA-z]', self.title)) > .6*len(self.title)
    
    def append_author(self, author, commit=True):
        """Append author to current publication and 
        preserve author order in it.
        """
        if db.session.query(author_publication).\
                filter(author_publication.c.publication_id == self.id).\
                filter(author_publication.c.author_id == author.id).first():
            return False
        max_o = db.session.query(func.max(author_publication.c.order)).\
                filter(author_publication.c.publication_id == self.id).\
                scalar() if db.session.query(author_publication).\
                filter(author_publication.c.publication_id == self.id).first() else\
                -1
        db.session.execute(insert(author_publication).\
                values([author.id,
                        author.main.id if author.main else author.id,
                        self.id,
                        max_o+1]))
        if commit:
            db.session.commit()
        return True


    def delete_author(self, author, commit=True):
        """Delete author from current publication"""
        db.session.execute(delete(author_publication).\
                where(author_publication.c.author_id==author.id).\
                where(author_publication.c.publication_id == self.id))
        if commit:
            db.session.commit()

    def change_raw_authors(self, raw_authors, delete_zero_authors=False):
        """Remove publication from previous parsed authors.
        If delete_zero_authors == True delete authors with 
        zero count publications. Parse new authors, and 
        append publication to these authors."""
        for author in self.authors:
            self.delete_author(author)
        if delete_zero_authors:
            for author in Author.query.all():
                if len(author.publications)==0:
                    db.session.delete(author)
        self.authors_raw = raw_authors
        self.parse_authors()


    def from_dict(self, data):
        output = {'reject': False,'message':'', 'warnings':''}
        if 'title' in data:
            if Publication.query.filter_by(title=data['title']).first():
                output['reject'] = True
                output['message'] = f"Publication already exist {data['title']}"
                return output, None
        if 'doi' in data and data['doi'] != '':
            if Publication.query.filter_by(doi=data['doi']).first():
                output['reject'] = True
                output['message'] =  f"Publication already exist. doi: {data['doi']}"
                return output, None
        for field in ['title', 'volume', 'issue', 'pages', 'year', 'doi']:
            if field in data:
                setattr(self, field, data[field])
        if 'pub_type' in data:
            self.pub_type = PubType(data['pub_type'])
        if 'journal' in data:
            journal = Journal.query.filter_by(title = data['journal']).first()
            if journal is None:
                journal = Journal(title=data['journal'])
                db.session.add(journal)
            self.journal = journal
        if 'authors_raw' in data:
            self.authors_raw = data['authors_raw']
            self.authors_raw = self.authors_raw.replace('and ',',').strip()
            self.authors_raw = self.authors_raw.replace(',,',',').strip()
            output['warnings'] += self.parse_authors() 
        return output, self

    def parse_authors(self):
        msg=''
        for author_raw in self.authors_raw.split(','):
            lastname, name, patr = Author.parse(author_raw)
            if any([lastname, name, patr]):
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
                    n='\n'
                    app.logger.info(f'AUTHOR ADDED:{n}{a.to_gost()}')
                self.append_author(a, False)
            else:
                msg += f"{author_raw} doesnt match to pattern" + "\n"
        return msg
    def to_dict(self):
        data={}
        for field in ['title', 'volume', 'issue', 'pages', 'year', 'doi', 'pub_type']:
            data[field] = getattr(self,field)
        data['authors'] = ', '.join([str(a) for a in self.authors])
        data['journal'] = self.journal.title if self.journal is not None else ''
        return(data)

    def to_gost(self):
        isen = self.isen()
        attr = []
        attr.append(self.journal.title if self.journal is not None else None)
        attr.append(self.year)
        attr.append(self.volume)
        attr.append(self.issue)
        attr.append("С. " + self.pages if self.pages is not None else None)
        attr = [str(a) for a in attr if a is not None and str(a).strip() not in ['','None','-']]
        try:
            output =(
                    f'{", ".join([a.to_gost(not isen) for a in self.authors])} '
                    f'{self.title} // '
                    f'{". - ".join(attr)}'
                    )
        except:
            print(self.id, self.title, end=' ') 
            output = 'None'
        return output

    def __repr__(self):
        return self.to_gost()


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
        if Journal.query.filter_by(title=data['title']).count()>0:
            print('Journal already exist:',data['title'])
            return False

        for field in ['title', 'quartile_JCR', 'quartile_SJR', 'is_risc', 'is_scopus', 'is_wos']:
            if field in data:
                setattr(self, field, data[field])
        if 'quartile' in data:
            self.quartile_JCR = self.quartile_SJR = data['quartile']
        return True

    def to_dict(self):
        data={}
        for field in ['title', 'quartile_JCR', 'quartile_SJR', 'is_wos', 'is_scopus', 'is_risc']:
            data[field] = getattr(self,field)
        return(data)

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
    
    def set_main(self, main_author):
        """Set main author for current author.
        Perform FIO and enFIO join. Substitute publications ownership.
        """
        self.main = main_author
        if main_author is not None:
            for p in self.publications:
                db.session.execute(update(author_publication).\
                                where(author_publication.c.publication_id==p.id).\
                                where(author_publication.c.author_id==self.id).\
                                values(main_id=main_author.id))
            db.session.commit()
            for n in ['name', 'lastname', 'patronymic', 'ename', 'elastname', 'epatronymic']:
                if not getattr(self.main, n) and getattr(self, n):
                    setattr(self.main, n, getattr(self, n))
        else:
            for p in self.publications:
                db.session.execute(update(author_publication).\
                                where(author_publication.c.publication_id==p.id).\
                                where(author_publication.c.author_id==self.id).\
                                values(main_id=self.id))
            db.session.commit()

    def add_synonym(self, syn_author):
        """Add to current author its synonym.
        Append FIO and enFIO if needed. Join publications.
        """
        syn_author.set_main(self)

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
        ruath = bool(self.lastname)
        ruout = enout = None
        if ruath:
            ruout = (
                    f'{self.lastname} '
                    f'{self.name[0]}.'
                    f'{self.patronymic[0]+"." if self.patronymic not in [None,""," "] else ""}'
                    )
        if self.elastname:
            enout = (
                    f'{self.elastname} '
                    f'{self.ename[0]}.'
                    f'{self.epatronymic[0]+"." if self.epatronymic not in [None,"", " "] else ""}'
                    )
        if rus is None:
            return self.to_gost(ruath)
        elif rus:
            return ruout if ruout else enout
        elif not rus:
            return enout if enout else ruout

    def __repr__(self):
        return self.to_gost() 

    @staticmethod
    def parse(author_raw):
        author_raw = author_raw.strip(" \t\n")
        r = r"([\w\\\-'`]+(?:\.|\s)?)\s*([\w\-`]+(?:\.|\s))?\s*([\w\-`]+\.?)*"
        ms = re.match(r,author_raw)
        lastname, name, patr = [None]*3
        if ms:
            gr = [n for n in ms.groups() if n]
            try:
                if all(not n.endswith('.') for n in gr): # case everyone ends without point
                    if len(gr)<3:
                        try: # case Fedorov P|PP, P|PP Fedorov
                            g = gr.pop([n.isupper() for n in gr].index(True))
                            lastname, name, patr = gr[0], g[:1], g[1:]
                        except ValueError: 
                            m = [re.search(r'([A-ZА-Я][a-zа-я]*)\s*([A-ZА-Я][a-zа-я]*)?',n).groups() for n in gr]
                            if any(a[-1] is not None for a in m): # case PeA Fedorov, Fedorov PeA
                                g = m.pop([a[-1] is not None for a in m].index(True))
                                lastname, name, patr = m[0][0], g[:1][0], g[1:][0]
                            else: # case Pe Fedorov, Fedorov Pe, Petr Fedorov, Fedorov Petr
                                lastname, name = (m[0][0], m[1][0]) if len(m[0][0])>2 else (m[1][0], m[0][0])
                    else: # Petr A Fedorov, Fedorov Petr A, Pe A Fedorov, Fedorov Pe A
                        maxs = [len(g) for g in gr]
                        lastname, name, patr = (gr[2], gr[0], gr[1]) if maxs.index(max(maxs))==2 else (gr[0], gr[1], gr[2])
                else: # P.P.|P. Fedorov, Fedorov P.P.|P., Pe.P.|Pe. Fedorov, Fedorov Pe.P.|Pe.
                    i = [g[-1]!='.' for g in gr].index(True)
                    if len(gr)<3:
                        g = gr.pop(i)
                        lastname, name = g, gr[0][:-1]
                    else:
                        g = gr.pop(i)
                        lastname, name, patr = g, gr[0][:-1], gr[1][:-1]
            except Exception as ex:
                print(f"While parsing {ex},  {author_raw}"+"\n")
        return lastname, name, patr



class Organisation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    authors = db.relationship('Author',
            secondary=author_organisation,
            backref='organisations')

    def __repr__(self):
        return self.title

class ExtPubColumn(db.Model):
    publication_id = db.Column(db.Integer, 
            db.ForeignKey('publication.id', name='publication_id_fk'), 
            primary_key=True)
    name = db.Column(db.String(255), primary_key=True)
    data = db.Column(db.String(2048))
    # publication

    def __repr__(self):
        return (f'[{self.publication_id},{self.name}]: {self.data}')

