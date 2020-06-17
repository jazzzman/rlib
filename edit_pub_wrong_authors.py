from app import app, db
from app.models import (Author, Publication, Journal, Organisation,
                        PubType, author_publication)
import random as rnd
import itertools as itt
from difflib import SequenceMatcher as sm
from sqlalchemy import delete
from sqlalchemy.sql.expression import func

pbs = Publication.query.filter_by(year=2019).all()
wrong_pubs = [p for p in pbs if len(p.authors)!=len(p.authors_raw.split(','))]

# preview parsed authors and raw authors
for wp in pbs:
    print('='*20+str(wp.id).ljust(40, '='))

    ar = [' '.join([a for a in Author.parse(raw) if a]) 
            for raw in wp.authors_raw.split(',')]
    ap = [(a.id,a.to_gost(not wp.isen())) for a in wp.authors]
    ar += ['']*(len(ap)-len(ar))
    ap += ['']*(len(ar)-len(ap))
    
    for i,z in enumerate(zip(ap,ar)):
        print(z[0][1].ljust(20),str(z[0][0]).ljust(4),str(i).ljust(2), z[1])
# preview author canidate in wrong pubs
# for wp in wrong_pubs:
    # print(''.ljust(40,'='))

    # ar = wp.authors_raw.split(',')
    # ap = [(a.id,a.to_gost(not wp.isen())) for a in wp.authors]

    # for pid, p in ap:
        # for a,r in itt.product([p],ar):
            # if sm(None,a,r).ratio()>0.5:
                # break
        # else:
            # print(wp.id, pid, p)

# delete wrong authors in pubs from file
# with open('wp.txt','r') as f:
    # lines =f.readlines()
    # for line in lines:
        # line = line.strip()
        # pid, aid = line.split(' ')
        # Publication.query.get(int(pid)).delete_author(Author.query.get(int(aid)))
        # db.session.commit()

# set order as it appears in association table
# for p in wrong_pubs:
    # sa = db.session.query(author_publication).\
            # filter(author_publication.c.publication_id==p.id).\
            # distinct().all()
    # sa = [list(r) for r in sa]
    # for i in range(len(sa)):
        # sa[i][2]=i

    # db.session.execute(delete(author_publication).\
            # where(author_publication.c.publication_id == p.id))

    # print('='*20)
    # for s in sa:
        # Publication.query.get(p.id).append_author(Author.query.get(s[0]))

    # print(*db.session.query(author_publication).\
            # filter(author_publication.c.publication_id==p.id).all(),
            # sep='\n')
    # db.session.commit()


