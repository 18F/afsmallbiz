from flask import Flask
import logging

__author__ = 'dwcaraway'
__credits__ = ['Dave Caraway']

log = logging.getLogger(__name__)

class DefaultConfig(object):
    MONGODB_SETTINGS = {
        'DB': 'pod',
        'USERNAME': 'admin',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': 27017
    }
    SECRET_KEY = "secret"
    DEBUG = True
    SECURITY_PASSWORD_HASH = 'bcrypt'
    SECURITY_REGISTERABLE = True
    SECURITY_PASSWORD_SALT = 'setyoursaltpasswordhere'
    SECURITY_CHANGEABLE = True
    SECURITY_RECOVERABLE = True

def create_app(config_object=DefaultConfig):
    app = Flask(__name__)

    #Flask application initialization
    app.config.from_object(config_object)

    #Data model initialization
    from sbir.model import db, User, Role
    db.init_app(app)

    #Security initialization
    from sbir.security import oauth, security
    from flask.ext.security import MongoEngineUserDatastore
    user_datastore = MongoEngineUserDatastore(db, User, Role)
    oauth.init_app(app)
    security.init_app(app, user_datastore)

    #Flask blueprint registration
    from sbir.web import api
    app.register_blueprint(api)

    return app
