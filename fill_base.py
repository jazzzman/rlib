from app import app, db
from app.models import (Author, Publication, Journal, Organisation,
                        AuthorSynonym, PubType)
import random as rnd

pubs = []
ptypes = [p for p in PubType]
for i in range(4,25):
    pubs.append(Publication(title=f'Publication {i}',
        authors_raw=', '.join([f'a{a}' for a in range(rnd.randint(1,12))]),
        year=rnd.randint(1990,2021),pub_type = rnd.choice(ptypes)))

jrs = []
for i in range(4,25):
    jrs.append(Journal(title=f'Journal {i}'))

aths = []
for i in range(4,25):
    aths.append(Author(name=f'AN{i}', 
        lastname=f'LN{i}',))

asys = []
for i, a in enumerate(aths):
    asys.append(AuthorSynonym(name=a.name, lastname=a.lastname, 
        main=a if i < 7 else rnd.choice(aths[:7])))

db.session.add_all(pubs)
db.session.add_all(jrs)
db.session.add_all(aths)
db.session.add_all(asys)
db.session.commit()

for ath in aths:
    ath.publications.extend(rnd.sample(pubs, 4))

for jr, pub in zip(jrs,pubs):
    jr.publications.append(pub)




db.session.commit()
print(pubs)
