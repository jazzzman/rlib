from app import app, db
from app.models import (Author, Publication, Journal, Organisation,
                        PubType)
import re

dump = r'misc\dump_mysql_publications.txt'

with open(dump,'r', encoding='utf8') as base:
    data = base.readlines()[14].split('),(')
    for p in data[:4]:
        p = p.lstrip('(').replace('\n','')
        r=r"(\d+),'(.*?)',(\-?\d+),'(.*?)','(.*?)',(\-?\d+),'(.*?)','(.*?)','(.*?)'"
        mc = re.match(r,p)
        if mc:
            gr=mc.groups()
            a=Publication()
            a.from_dict({
                'title': gr[1],
                'volume': gr[2],
                'issue': gr[3],
                'pages': gr[4],
                'year': gr[5],
                'doi': gr[6],
                'authors_raw': gr[7],
                'pub_type': PubType[gr[8]],
                })
            db.session.add(a)
        else:
            print(p)


