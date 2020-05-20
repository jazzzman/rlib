from app import app, db
from app.models import (Journal, Publication, Author, PubType, 
                        ExtPubColumn, author_publication)
from sqlalchemy.orm.query import Query

@app.shell_context_processor
def make_shell_context():
    return {'db': db,
            'pb': Publication,
            'jr': Journal,
            'au': Author,
            'pt': PubType,
            'ec': ExtPubColumn,
            'rap': author_publication,
            }
