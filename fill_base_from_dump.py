from app import app, db
from app.models import (Author, Publication, Journal, Organisation,
                        PubType)
import re
import sys

def clear_data(session):
    meta = db.metadata
    for table in reversed(meta.sorted_tables):
        print(f'Clear table {table}')
        session.execute(table.delete())
    session.commit()


clear_data(db.session)

dpubs = open(r'misc/dump_mysql_publications.txt', 'r', encoding='utf8')
drpj = open(r'misc/dump_mysql_relation_journal_publication.txt', 'r', encoding='utf8')
djours = open(r'misc/dump_mysql_journals.txt', 'r', encoding='utf8')

data = drpj.readline()
rel_jp_dict = re.findall(r'\d+,\d+',data)
rel_pj = { kvp.split(',')[1].strip() : kvp.split(',')[0].strip() for kvp in rel_jp_dict}

data = djours.readline()
rawl = data.split('),(')
r = r"(\d+),'(.*)',(-?\d+),(\d),(\d),(\d)"
for l in rawl:
    l = l.lstrip('(')
    mc = re.match(r,l)
    if mc:
        gr = mc.groups()
        data = {
            'idd': gr[0],
            'title': gr[1],
            'quartile_SJR': gr[2],
            'quartile_JCR': gr[2],
            'is_wos': bool(int(gr[3])),
            'is_scopus': bool(int(gr[4])),
            'is_risc': bool(int(gr[5]))
            }
        for k,v, in rel_pj.items():
            if v == gr[0]:
                rel_pj[k]=gr[1]
        j = Journal()
        j.from_dict(data)
        db.session.add(j)
    else:
        print(l)

data = dpubs.readlines()[14].split('),(')
for p in data:
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
            'year': int(gr[5]),
            'doi': gr[6],
            'authors_raw': gr[7],
            'pub_type': PubType[gr[8]],
            'journal': rel_pj[gr[0]]
            })
        db.session.add(a)
    else:
        print(p)

db.session.commit()


