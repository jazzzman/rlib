from app import app, db
from app.models import Journal, Publication, Author


@app.shell_context_processor
def make_shell_context():
    return {'db': db,
            'pb': Publication,
            'jr': Journal,
            'au': Author}
