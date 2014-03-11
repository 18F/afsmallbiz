import random
from flask import current_app

__author__ = 'dwcaraway'
__credits__ = 'Dave Caraway'

# Set Path
# pwd = os.path.abspath(os.path.dirname(__file__))
# project = os.path.basename(pwd)
# new_path = pwd.strip(project)
# activate_this = os.path.join(new_path, 'sbir')
# sys.path.append(activate_this)

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

MONGO_DATABASE = 'pod_behave_' + str(random.randint(2000, 5000))


class BehaveConfig(object):
    MONGODB_SETTINGS = {
        'DB': MONGO_DATABASE,
        'USERNAME': 'admin',
        'PASSWORD': '',
        'HOST': 'localhost',
        'PORT': 27017
    }
    SECRET_KEY = 'secret_key'
    DEBUG = True
    TEST = True
    SECURITY_PASSWORD_HASH = 'bcrypt'
    SECURITY_REGISTERABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_RECOVERABLE = True
    SECURITY_PASSWORD_SALT = 'password_salt'


class FlaskTestClientProxy(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        environ['REMOTE_ADDR'] = environ.get('REMOTE_ADDR', '127.0.0.1')
        environ['HTTP_USER_AGENT'] = environ.get('HTTP_USER_AGENT', 'Chrome')
        return self.app(environ, start_response)


def before_scenario(context, feature):
    from sbir import create_app
    app = create_app(BehaveConfig)
    app.wsgi_app = FlaskTestClientProxy(app.wsgi_app)
    context.app = app
    context.client = app.test_client()


def after_scenario(context, feature):
    mongoengine = get_extension(context, 'mongoengine')
    if mongoengine:
        mongoengine.connection.drop_database(MONGO_DATABASE)


def get_extension(context, feature):
    app = context.app
    with app.app_context():
        extensions = getattr(current_app, 'extensions', {})
        if feature in extensions:
            return extensions[feature]
    return None
