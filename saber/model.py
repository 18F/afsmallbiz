import datetime
from flask.ext.mongoengine import MongoEngine, Document, DynamicDocument
from flask.ext.security import RoleMixin, UserMixin
from mongoengine import StringField, EmailField, DateTimeField, ListField, ReferenceField, BooleanField, URLField

__author__ = 'dwcaraway'
__credits__ = ['Dave Caraway']

db = MongoEngine()


class Role(Document, RoleMixin):
    """
    A user's security role
    """
    name = StringField(max_length=80, unique=True)
    description = StringField(max_length=255)

    def __unicode__(self):
        return self.name


class User(Document, UserMixin):
    """
    A user in the system
    """
    password = StringField(max_length=255, required=True)  # a hash of the user's password
    email = EmailField(max_length=255, required=True, unique=True)
    display_name = StringField(max_length=255, required=True)
    created_at = DateTimeField(default=datetime.datetime.now, required=True)
    updated_at = DateTimeField(default=datetime.datetime.now)
    logged_in_at = DateTimeField(default=datetime.datetime.now)
    roles = ListField(ReferenceField(document_type=Role), default=[])
    active = BooleanField(default=True)
    confirmed_at = DateTimeField()

    meta = {
        'collection': 'users',
        'indexes': ['-created_at', 'email'],
        'ordering': ['email']
    }

    def __unicode__(self):
        return self.email


class Client(Document):
    """
    An API OAuth v1 client
    """
    user = ReferenceField(document_type='User', required=True)
    client_key = StringField(required=True)
    client_secret = StringField(required=True)
    realms = ListField(StringField(), default=[])
    redirect_uris = ListField(StringField(), default=[])

    meta = {
        'collection': 'clients',
        'indexes': ['client_key', 'user']
    }


class RequestToken(Document):
    """
    One-time request and verifier token. Request token is designed for exchanging access token. Verifier token is
    designed to verify the current user. It is always suggested that you combine request token and verifier together.
    """
    #TODO store in cache
    user = ReferenceField(document_type='User', required=True)
    client = ReferenceField(document_type='Client', required=True)
    token = StringField(unique=True, required=True)
    secret = StringField(required=True)
    verifier = StringField()
    redirect_uri = URLField()
    realms = ListField(StringField(), default=[])


class Nonce(Document):
    """
    Timestamp and nonce is a token for preventing repeating requests. The time life of a timestamp and nonce
    is 60 seconds
    """
    #TODO store in cache
    timestamp = DateTimeField(default=datetime.datetime.now, required=True)
    nonce = StringField()
    client = ReferenceField(Client, required=True)
    request_token = StringField()
    access_token = StringField()

class AccessToken(Document):
    """
    An access token is the final token that could be use by the client. Client will send access token every time when it
    needs to access a resource.
    """
    client = ReferenceField(document_type='Client', required=True)
    user = ReferenceField(document_type='User')  # TODO is this required? client has the user too
    token = StringField(required=True)  # Access Token
    secret = StringField(required=True)  # Access token secret
    realms = ListField(StringField(), default=True)  # Realms with this access token

class Schema(Document):
    """
    JSON schema referenced by other resources in the system.
    """
    created_at = DateTimeField(default=datetime.datetime.now, required=True)
    created_by = ReferenceField(document_type=User, required=True)
    last_modified_at = DateTimeField(default=datetime.datetime.now, required=True)
    last_modified_by = ReferenceField(document_type=User, required=True)
    text = StringField(required=True)  # the actual JSON schema text
