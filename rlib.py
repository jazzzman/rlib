from app import app, db
from app.models import Journal, Publication, Author
from sqlalchemy.orm.query import Query

@app.shell_context_processor
def make_shell_context():
    db.session.enable_baked_queries = True
    db.session._query_cls = Query
    return {'db': db,
            'pb': Publication,
            'jr': Journal,
            'au': Author}
