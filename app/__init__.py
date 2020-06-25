from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from logging.handlers import RotatingFileHandler
from flask_bootstrap import Bootstrap
import logging
import os
import app.filters


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = 'auth.signin'
bootstrap = Bootstrap()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    with app.app_context():
        db.session.execute('pragma foreign_keys=ON') # for cascade deleting from 
                                                 # tables in case of SQLLite db
    migrate.init_app(app,db)
    login.init_app(app)
    bootstrap.init_app(app)

    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp)

    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    app.register_blueprint(filters.bp)

    if app.config['TESTING']:
        app.testing = True

    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/rlib.log', maxBytes=10240,
                                           backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)

    return app


from app import models

def url_for_static(filename):
    root = app.config.get('STATIC_ROOT', '')
    return join(root, filename)
