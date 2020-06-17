from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from logging.handlers import RotatingFileHandler
from flask_bootstrap import Bootstrap
import logging
import os


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
db.session.execute('pragma foreign_keys=ON') # for cascade deleting from 
                                             # tables in case of SQLLite db
migrate = Migrate(app, db)
login = LoginManager(app)
bootstrap = Bootstrap(app)

from app import routes, models

if not os.path.exists('logs'):
    os.mkdir('logs')
file_handler = RotatingFileHandler('logs/rlib.log', maxBytes=10240,
                                   backupCount=10)
file_handler.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
file_handler.setLevel(logging.INFO)
app.logger.addHandler(file_handler)

app.logger.setLevel(logging.INFO)

if not app.debug:
    pass

def url_for_static(filename):
    root = app.config.get('STATIC_ROOT', '')
    return join(root, filename)
