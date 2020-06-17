from app import app, db
from app.models import (Author, Publication, Journal, Organisation,
                        PubType, ExtPubColumn)
import re
import sys
import pandas as pd
from difflib import SequenceMatcher as SM


#pubs
cols = {
        'authors':0,
        'title':1,
        'journal':2,
        'VIP':3,
        'DOI':4,
        'Q':5,
        }
#thesis
# cols = {
        # 'authors':0,
        # 'title':1,
        # 'journal':2,
        # 'location':4,
        # 'date':3,
        # 'VIP':5,
        # # 'DOI':6,
        # }


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
    m = re.search(r'\s*(\d+)\s*(?:\(([\d-]+)\)[,:]?)?\s+([\da-zA-z-]+)\s*(\(\d{3,4}\))?',text)
    if 'направлена в редакцию' in text or 'принята к печати' in text:
        return [None]*3
    elif not m:
        print('Don\'t understand input:',text)
        s = input('Insert manual Vol Issue Pages. Field separator space:')
        return (s.split()+[None]*3)[:3]
    return m.groups()[0],m.groups()[1], m.groups()[2]


PUBTYPE = PubType.Proceedings
fn = 'misc/просидинги 2016.txt'
YEAR = int(re.findall(r'\d{4}', fn)[0])
with open(fn,'r') as file:
    pubs = file.readlines()
pubs = [p.strip(' \t\n,') for p in pubs]

# initial author parsing check
# for i in range(0,len(pubs),6):
    # row=pubs
    # print('\n',i,row[i+cols['title']])
    # author_raw = row[i+cols['authors']]
    # author_raw = re.sub('\d','',author_raw)
    # author_raw = re.sub(' and ',',',author_raw)
    # author_raw = re.sub(' и ',',',author_raw)
    # author_raw = re.sub(',,',',',author_raw)
    # for a in author_raw.split(','):
        # print(Author.parse(a))
# sys.exit()

# with db.session.no_autoflush:
for i in range(0,len(pubs),6):
    row = pubs
    print(i, row[i+cols['title']],end=' ')

    # if any(SM(None,p.title.lower(), row[i+cols['title']].lower()).ratio() >0.97 for p in Publication.query.all()):
        # print('EXISTS')
        # continue
    # print(i)
    # continue
    jr = Journal()
    qq = get_Q(row[i+cols['Q']] if PUBTYPE == PubType.Article else '')
    if jr.from_dict({
        'title': row[i+cols['journal']],
        'quartile_SJR': qq[3],
        'quartile_JCR': qq[1],
        'is_wos': qq[0],
        'is_scopus': qq[2],
        'is_risc': qq[4]
        }):
        db.session.add(jr)
    else:
        jr = Journal.query.filter_by(title=row[i+cols['journal']]).first()
        # jr.quartile_JCR = int(qq[1])
        # jr.quartile_SJR = int(qq[3])
        # jr.is_wos = qq[0]
        # jr.is_scopus = qq[2]
        # jr.is_risc = qq[4]

    if any(SM(None,p.title.lower(), row[i+cols['title']].lower()).ratio() >0.97 for p in Publication.query.all()):
        print('EXISTS')
        continue
    print()

    pb = Publication()
    vip = get_VIP(row[i+cols['VIP']]) if PUBTYPE == PubType.Article else [0,'-',row[i+cols['VIP']]]
    vip = list(vip)
    tvip = row[i+cols['VIP']].split()
    if len(tvip) == 2:
        vip[0], vip[2] = tvip
    elif len(tvip) == 3:
        vip[0], vip[1], vip[2] = tvip
    resp, _ = pb.from_dict({
        'title': row[i+cols['title']],
        'volume': vip[0],
        'issue': vip[1],
        'pages': vip[2],
        'year': YEAR,
        'doi': row[i+cols['DOI']],
        'authors_raw': row[i+cols['authors']],
        'pub_type': PUBTYPE, 
        'journal': jr.title
        })
    if PUBTYPE == PubType.ConfThesis:
        pb.add_fields.append(ExtPubColumn(name='Location',data=row[i+cols['location']]))
        # pb.add_fields.append(ExtPubColumn(name='ConfThesisType',data=row[i+cols['thesis_type']]))
        pb.add_fields.append(ExtPubColumn(name='Date',data=row[i+cols['date']]))
    db.session.add(pb)
    print('' if resp['reject'] else resp['message'])

db.session.commit()
print(Publication.query.filter_by(title=None).count(),'empty rows were deleted')
Publication.query.filter_by(title=None).delete()
db.session.commit()
