from app import app, db
from app.models import (Author, Publication, Journal, Organisation,
                        PubType, author_publication)
import random as rnd
import re
import itertools as itt
from difflib import SequenceMatcher as sm
from sqlalchemy import delete
from sqlalchemy.sql.expression import func


ids = [1150]

for id in ids:
    r = Publication.query.get(id).authors_raw
    nr = re.sub(r'([a-zA-z]+)\s+(?:[A-Z]\.\s*){,3}\s*([a-zA-Z]+)\s*',r'\2 \1',r)
    print(r,'\n',nr)
    # Publication.query.get(id).change_raw_authors(nr,True)

db.session.commit()
