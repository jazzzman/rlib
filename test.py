import unittest
import re
from app import app, db
from app.models import Author, Publication, Journal, Organisation


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

class MainAuthorSetting(unittest.TestCase):
    def setUp(self):
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        db.create_all()
    def tearDown(self):
        db.session.remove()

    def test_main_set(self):
        a1 = Author(name='1',lastname='L1')
        a2 = Author(name='2',lastname='L2')
        a3 = Author(name='3',lastname='L3')
        pb1 = Publication(title='Pb1')
        pb2 = Publication(title='Pb2')
        db.session.add_all([a1,a2,a3,pb1,pb2])
        pb1.authors.extend([a1,a3])
        pb2.authors.extend([a2])
        print(a1.publications)
        print(a2.publications)
        print(a3.publications)
        print(pb1.authors)
        print(pb2.authors)
        a3.set_main(a2)
        print(a1.publications)
        print(a2.publications)
        print(a3.publications)
        print(pb1.authors)
        print(pb2.authors)
        a3.set_main(None)
        print(a1.publications)
        print(a2.publications)
        print(a3.publications)
        print(pb1.authors)
        print(pb2.authors)

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

        


if __name__ == '__main__':
    unittest.main(verbosity=2)



