from app import app, db
from app.models import (Author, Publication, Journal, Organisation,
                        PubType, ExtPubColumn)
import re
import sys
import pandas as pd


#pubs
cols = {
        'authors':1,
        'title':2,
        'journal':3,
        'VIP':4,
        'DOI':5,
        'Q':6,
        }
#thesis
cols = {
        'authors':1,
        'title':2,
        'journal':3,
        'location':4,
        'date':5,
        'VIP':6,
        'thesis_type':7,
        'DOI':8,
        }


def get_Q(text):
    if not text:
        return (False,0,False,0,False)
    if text.count('/') == 2:
        summary = []
        qs = text.split('/')
        for q in qs:
            q = q.strip()
            if q[0] == 'Q':
                summary.extend([True,q[-1]])
            elif 'нет Q' in q:
                summary.extend([True,0])
            elif 'РИНЦ' in q:
                summary.extend(['не' in q])
            else:
                summary.extend([False,0])
        return summary
    QW = re.match(r'^Q\d',text)
    isW = re.match(r'нет Q',text)
    isR = re.search('РИНЦ', text)
    QS = re.search(r'SJR\s*-\s*Q\d',text)
    return ((QW or isW) is not None, 
            QW.group()[-1] if QW is not None else 0,
            QS is not None,
            QS.group()[-1] if QS is not None else 0,
            isR is not None)

def get_VIP(text):
    m = re.search(r'\s*(\d+)\s*(?:\(([\d-]+)\)[,:]?)?\s+([\da-zA-z-]+)\s*(\(\d{2,4}\))?',text)
    if 'направлена в редакцию' in text or 'принята к печати' in text:
        return [None]*3
    elif not m:
        print('Don\'t understand input:',text)
        s = input('Insert manual Vol Issue Pages. Field separator space:')
        return (s.split()+[None]*3)[:3]
    return m.groups()[0],m.groups()[1], m.groups()[2]


PUBTYPE = PubType.ConfThesis 
YEAR = 2018
pubs = pd.read_csv('misc/тезисы 2018.csv')
pubs = pubs.fillna('')

# initial author parsing check
# for i,row in pubs.iterrows():
    # print('\n',i,row[cols['title']])
    # author_raw = row[cols['authors']]
    # author_raw = re.sub('\d','',author_raw)
    # author_raw = re.sub(' and ',',',author_raw)
    # author_raw = re.sub(' и ',',',author_raw)
    # author_raw = re.sub(',,',',',author_raw)
    # for a in author_raw.split(','):
        # print(Author.parse(a))
# sys.exit()

for i,row in pubs.iterrows():
    print(i, row[cols['title']],end=' ')
    jr = Journal()
    qq = get_Q(row[cols['Q']] if PUBTYPE == PubType.Article else '')
    if jr.from_dict({
        'title': row[cols['journal']],
        'quartile_SJR': qq[3],
        'quartile_JCR': qq[1],
        'is_wos': qq[0],
        'is_scopus': qq[2],
        'is_risc': qq[4]
        }):
        db.session.add(jr)
    else:
        jr = Journal.query.filter_by(title=row[cols['journal']]).first()
        jr.quartile_JCR = int(qq[1])
        jr.quartile_SJR = int(qq[3])
        jr.is_wos = qq[0]
        jr.is_scopus = qq[2]
        jr.is_risc = qq[4]

    if Publication.query.filter_by(title=row[cols['title']]).scalar() is not None:
        print('EXISTS')
        continue
    print()

    pb = Publication()
    vip = get_VIP(row[cols['VIP']]) if PUBTYPE == PubType.Article else [0,'-',row[cols['VIP']]]
    resp, _ = pb.from_dict({
        'title': row[cols['title']],
        'volume': vip[0],
        'issue': vip[1],
        'pages': vip[2],
        'year': YEAR,
        'doi': row[cols['DOI']],
        'authors_raw': row[cols['authors']],
        'pub_type': PUBTYPE, 
        'journal': jr.title
        })
    if PUBTYPE == PubType.ConfThesis:
        pb.add_fields.append(ExtPubColumn(name='Location',data=row[cols['location']]))
        pb.add_fields.append(ExtPubColumn(name='ConfThesisType',data=row[cols['thesis_type']]))
        pb.add_fields.append(ExtPubColumn(name='Date',data=row[cols['date']]))
    db.session.add(pb)
    print('' if resp['reject'] else resp['message'])

db.session.commit()
print(Publication.query.filter_by(title=None).count(),'empty rows were deleted')
Publication.query.filter_by(title=None).delete()
db.session.commit()
