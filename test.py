import unittest
import re
from app import app, db
from app.models import (Author, Publication, Journal, 
        Organisation, ExtPubColumn, author_publication)
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, update, insert
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import func

class Relations(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_authorpublication(self):
        p1 = Publication(title='p1', authors_raw='a1, a2, a3')
        p2 = Publication(title='p2', authors_raw='a2, a3')
        p3 = Publication(title='p3', authors_raw='a1, a3')
        db.session.add_all([p1, p2, p3])
        db.session.commit()
        self.assertEqual(p1.authors, [])
        a1 = Author(name='a', lastname='a1')
        a2 = Author(name='b', lastname='a2')
        a3 = Author(name='c', lastname='a3')
        db.session.add_all([a1, a2, a3])
        db.session.commit()
        self.assertEqual(a1.publications, [])
        a1.publications.append(p1)
        a1.publications.append(p3)
        a2.publications.append(p1)
        a3.publications.append(p1)
        db.session.commit()
        self.assertEqual(p1.authors, [a1, a2, a3])
        self.assertEqual(p3.authors, [a1])

    def test_authororganisation(self):
        a1 = Author(name='a', lastname='a1')
        a2 = Author(name='b', lastname='a2')
        a3 = Author(name='c', lastname='a3')
        db.session.add_all([a1, a2, a3])
        db.session.commit()
        o1 = Organisation(title='o1')
        o2 = Organisation(title='o2')
        o3 = Organisation(title='o3')
        db.session.add_all([o1, o2, o3])
        db.session.commit()
        a1.organisations.append(o1)
        a1.organisations.append(o2)
        a2.organisations.append(o2)
        db.session.commit()
        self.assertEqual(o3.authors, [])
        self.assertEqual(o1.authors, [a1])
        self.assertEqual(o2.authors, [a1, a2])
        o3.authors.extend([a2, a3])
        db.session.commit()
        self.assertEqual(o3.authors, [a2, a3])

    def test_publicationjournal(self):
        p1 = Publication(title='p1', authors_raw='a1, a2, a3')
        p2 = Publication(title='p2', authors_raw='a2, a3')
        p3 = Publication(title='p3', authors_raw='a1, a3')
        db.session.add_all([p1, p2, p3])
        db.session.commit()
        j1 = Journal(title='j1')
        j2 = Journal(title='j2')
        j3 = Journal(title='j3')
        db.session.add_all([j1, j2, j3])
        db.session.commit()
        j1.publications.append(p1)
        j2.publications.extend([p2, p3])
        db.session.commit()
        self.assertEqual(p1.journal, j1)
        self.assertEqual(p2.journal, j2)
        self.assertEqual(p3.journal, j2)
        self.assertEqual(j3.publications.all(), [])
        self.assertEqual(p1.journal_id, j1.id)


class RegexAuthors(unittest.TestCase):
    def test_authors_parser(self):
        with open(r'misc\authors_raw.txt', 'r') as alines:
            for authors_raw in alines.readlines():
                for author_raw in authors_raw.split(','):
                    r = r"([\w\-'`]+)\.?\s*([\w\-`]+)?\.?\s*([\w\-`]+)*"
                    ms = re.match(r,author_raw)
                    if ms:
                        lastname, name, patr = ms.groups()
                        if len(lastname)<2 and patr is not None:
                            lastname, name, patr = patr, lastname, name
                        elif len(lastname)<2 and patr is None:
                            lastname, name, patr = name, lastname, patr
                        elif len(lastname)<3 and lastname.isupper():
                            lastname, name, patr = name, lastname[0], lastname[1]
                        elif len(name)==2 and name.isupper():
                            lastname, name, patr = lastname, name[0], name[1]                       # print(author_raw, lastname, name, patr)


class PublicationAdding(unittest.TestCase):
    def tearDown(self):
        db.session.remove()

    def test_by_json(self):
        pb = Publication()
        data = {
            "title": "NewP4ublication",
            "journal": "Journal 9",
            "authors_raw": "LN17 AN17, LN14 AN14"
        }
        self.assertEqual(pb.from_dict(data), True)
        print(pb.authors)

    def test_json_author_exist(self):
        pb = Publication()
        data = {
            "title": "NewNwPublication",
            "journal": "Journal 9",
            "authors_raw": "LN17 AN7, N14 AN14"
        }
        self.assertEqual(pb.from_dict(data), True)
        print(pb.authors)
    
    def test_json_publ_exist(self):
        pb = Publication()
        data = {
            "title": "Publication 23",
            "journal": "Journal 9",
            "authors_raw": "LN17 AN7, N14 AN14"
        }
        self.assertEqual(pb.from_dict(data), False)
        print(pb.authors)


class EnRuToGOST(unittest.TestCase):
    def test_RuAuthor(self):
        a1 = Author(name='1',lastname='Ф1')
        self.assertEqual(a1.to_gost(),'Ф1 1.')
        self.assertEqual(a1.to_gost(True),'Ф1 1.')
        self.assertEqual(a1.to_gost(False),'Ф1 1.')
        a1.patronymic = 'О'
        self.assertEqual(a1.to_gost(),'Ф1 1.О.')
        self.assertEqual(a1.to_gost(True),'Ф1 1.О.')
        self.assertEqual(a1.to_gost(False),'Ф1 1.О.')
        a1.elastname = 'L1'
        a1.ename = 'Name'
        a1.epatronymic = 'Patr'
        self.assertEqual(a1.to_gost(),'Ф1 1.О.')
        self.assertEqual(a1.to_gost(True),'Ф1 1.О.')
        self.assertEqual(a1.to_gost(False),'L1 N.P.')

    def test_EnAuthor(self):
        a1 = Author(ename='1',elastname='L1')
        self.assertEqual(a1.to_gost(),'L1 1.')
        self.assertEqual(a1.to_gost(True),'L1 1.')
        self.assertEqual(a1.to_gost(False),'L1 1.')
        a1.epatronymic = 'P'
        self.assertEqual(a1.to_gost(),'L1 1.P.')
        self.assertEqual(a1.to_gost(True),'L1 1.P.')
        self.assertEqual(a1.to_gost(False),'L1 1.P.')
        a1.lastname = 'Ф1'
        a1.name = 'Имя'
        a1.patronymic = 'Отч'
        self.assertEqual(a1.to_gost(),'Ф1 И.О.')
        self.assertEqual(a1.to_gost(True),'Ф1 И.О.')
        self.assertEqual(a1.to_gost(False),'L1 1.P.')


class MainAuthorSetting(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_main_set(self):
        a1 = Author(name='1',lastname='La0101')
        a2 = Author(name='2',lastname='La0102', ename='Ru0102')
        a3 = Author(name='3',lastname='La0201')
        a4 = Author(name='4',lastname='La0202', ename='Ru0202')
        pb1 = Publication(title='Pb1')
        pb2 = Publication(title='Pb2')
        db.session.add_all([a1,a2,a3,a4,pb1,pb2])
        pb1.authors.extend([a1,a3])
        pb2.authors.extend([a2,a4])
        db.session.commit()
        self.assertEqual(pb1.authors,[a1,a3])
        self.assertEqual(a4.publications,[pb2])
        a2.set_main(a1)
        db.session.commit()
        self.assertEqual(a1.ename,a2.ename)
        self.assertEqual(a1.publications,[pb1,pb2])
        self.assertEqual(a2.publications,[])
        self.assertEqual(list(pb1.authors),[a1,a3], 
                msg="Author Order corrupt")
        self.assertEqual(list(pb2.authors),[a1,a4])
        # print('a1 syn:',a1.synonym)
        # print('a1 main:',a1.main)
        # print('a2 syn:',a2.synonym)
        # print('a2 main:',a2.main)
        # print('a1 elastname:', a1.elastname)
        # print(a1.publications)
        # print(a2.publications)
        # print(a3.publications)
        # a3.set_main(None)
        # print(a1.publications)
        # print(a2.publications)
        # print(a3.publications)
        # print(pb1.authors)
        # print(pb2.authors)

    def test_add_synonym(self):
        a1.add_synonym(a2)
        pass


class exportGOST(unittest.TestCase):
    def setUp(self):
        # app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()
    def tearDown(self):
        db.session.remove()

    def test_export(self):
        print(Author.query.all())
        a1 = Author.query.get(5)
        a2 = Author.query.get(795)
        print(a1.to_gost())
        print(a1.to_gost(True))
        print(a1.to_gost(False))
        print(a2.to_gost())
        print(a2.to_gost(True))
        print(a2.to_gost(False))
        p1 = Publication.query.get(319)
        p2 = Publication.query.get(320)
        print(p1.to_gost())
        print(p2.to_gost())


class AdditionalPublicationColumns(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
    
    def test_adding_columns(self):
        pb1 = Publication(title='Pb1')
        pb2 = Publication(title='Pb2')
        db.session.add_all([pb1,pb2])
        db.session.commit()
        adf1= ExtPubColumn(name='f1',data='pb1_f1_data1')
        pb2.add_fields.append(ExtPubColumn(name='f2', data='pb2_f2_data2'))
        pb1.add_fields.append(ExtPubColumn(name='f2', data='pb1_f2_data1'))
        pb1.add_fields.append(adf1)
        db.session.add(adf1)
        db.session.commit()
        print(ExtPubColumn.query.all())
        print(ExtPubColumn.query.filter_by(name='f2').all())

class AutoIncrTwoIndexes(unittest.TestCase):
    def test_creation_specific_table(self):
        engine = create_engine('sqlite:///')
        meta = MetaData()
        t = Table('test', meta,
                db.Column('o_id', db.Integer,primary_key = True),
                db.Column('p_id', db.Integer,primary_key = True),
                db.Column('a_id',db.Integer, primary_key = True))
        meta.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        conn = engine.connect()

        conn.execute(t.insert().values({'o_id':1,'p_id':0,'a_id':0}))
        conn.execute(t.insert().values({'o_id':0,'p_id':0,'a_id':1}))
        conn.execute(t.insert().values({'o_id':2,'p_id':1,'a_id':4}))
        conn.execute(t.insert().values({'o_id':3,'p_id':1,'a_id':1}))
        session.commit()
        print()
        print(*session.query(t).filter(t.c.p_id==0).order_by('o_id').all(),sep='\n')
        print("=====================")
        print(*session.query(t).order_by('o_id').all(),sep='\n')
        conn.execute(update(t).where(t.c.a_id==1).values(a_id=3))
        print("=====================")
        print(*session.query(t).order_by('o_id').all(),sep='\n')

class PublicationWithSortedAuthors(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()
    def tearDown(self):
        db.session.remove()

    def test_adding_publications(self):
        print()
        a1 = Author(name='O', lastname='Last1')
        a2 = Author(name='O', lastname='Last2')
        a3 = Author(name='O', lastname='Last3')
        p1 = Publication(title='Publication1')
        p2 = Publication(title='Publication2')
        db.session.add_all([a1,a2,a3,p1,p2])
        db.session.commit()
        p1.append_author(a1)
        p1.append_author(a2)
        self.assertEqual(p1.authors,[a1,a2])
        a1.set_main(a3)
        self.assertEqual(p1.authors,[a3,a2])
        self.assertEqual(a1.publications,[])
        self.assertEqual(a3.publications,[p1])


class PublicationFiltering(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()
    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_filter_by_author_id(self):
        aths, pbs = [], []
        for i in range(200):
            aths.append(Author(name="A",lastname=f'LastName{i}'))
        for i in range(50):
            pbs.append(Publication(title=f'Publication{i}'))
        db.session.add_all(pbs)
        db.session.add_all(aths)
        db.session.commit()

        for i in range(5):
            pbs[0].append_author(aths[i])
            pbs[1].append_author(aths[i])
        db.session.commit()

        a1, a2, a3 = aths[:3]
        al = aths[-1]
        p1, p2 = pbs[:2]
        pl = pbs[-1]
        pl.append_author(al)
        db.session.commit()

        self.assertEqual(Publication.query.join(Publication.authors).\
                filter(Author.id.in_([a1.id])).all(),[p1,p2])
        self.assertEqual(Publication.query.join(Publication.authors).\
                filter(Author.id.in_([al.id])).all(),[pl])
        self.assertEqual(len(Publication.query.join(Publication.authors).\
                filter(Author.id.in_([a2.id])).all()),2)
        self.assertEqual(len(Publication.query.join(Publication.authors).\
                filter(Author.id.in_([a1.id,al.id])).all()),len(pbs[:2]+[pl]))
        self.assertEqual(Publication.query.join(Publication.authors).\
                filter(Author.id.in_([a1.id,al.id])).count(),len(pbs[:2]+[pl]))
        self.assertCountEqual(Publication.query.all(),pbs)
        self.assertEqual(len(Publication.query.all()),
                        Publication.query.\
                            paginate(1,5,False).total)
        self.assertEqual(Publication.query.count(),
                        Publication.query.\
                            paginate(1,5,False).total)
        self.assertEqual(3,len([p for p in pbs if p.authors])) 
        q = Publication.query.join(Publication.authors)
        print('\n',*db.session.execute(q.statement).fetchall(), sep='\n')
        print(q.statement)
        self.assertEqual(3,
                        Publication.query.\
                            join(Publication.authors).distinct().limit(4).count())
        self.assertEqual(3,
                        len(Publication.query.\
                            join(Publication.authors).distinct().limit(4).all()))
        self.assertEqual(3,
                        Publication.query.\
                            join(Publication.authors).distinct().\
                            paginate(1,5,False).total)
    
        
class JoiningTutorial(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()
    def tearDown(self):
        db.session.remove()

    def test_cascade_deleting(self):
        p1= Publication(title='P1')
        p2= Publication(title='P2')
        db.session.add_all([p1,p2])
        db.session.commit()

        p1.add_fields.append(ExtPubColumn(name='f1', data='p1 f1'))
        p2.add_fields.append(ExtPubColumn(name='f1', data='p2 f1'))
        db.session.commit()

        print(ExtPubColumn.query.all())
        self.assertEqual(len(ExtPubColumn.query.all()),2)

        db.session.delete(p1)
        db.session.commit()
        print(ExtPubColumn.query.all())
        self.assertEqual(len(ExtPubColumn.query.all()),1)

        

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(JoiningTutorial)
    unittest.TextTestRunner(verbosity=2).run(suite)
    # unittest.main(verbosity=2)



