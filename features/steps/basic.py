
from behave import given, when, then
from dougrain import Document
from ..environment import get_extension
from flask.ext.security.utils import encrypt_password
import logging, json, string

__author__ = 'dwcaraway'
__credits__ = ['Dave Caraway']

logger = logging.getLogger(__name__)

resource = dict()
resource['root'] = '/'
resource['organization'] = '/organizations'
resource['dataset'] = '/datasets'
resource['user'] = '/users'
resource['schema'] = '/schema'

def get_url(label):
    assert string.strip(label), "empty label %s" % label
    if label in resource:
        return resource[label]
    raise Exception('Resource not found: "%s"' % label)

def get(context, url=None, follow_redirects=True):
    return context.client.get(url, follow_redirects=follow_redirects, environ_base={'HTTP_USER_AGENT': u'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'})

def put(context, url=None, data=dict(), follow_redirects=True):
    return context.client.put(
        url,
        data=data,
        follow_redirects=follow_redirects,
        environ_base={'HTTP_USER_AGENT': u'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'})

def post(context, url=None, data=dict(), follow_redirects=True):
    return context.client.post(
        url,
        data=data,
        follow_redirects=follow_redirects,
        environ_base={'HTTP_USER_AGENT': u'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'})

def delete(context, url=None, follow_redirects=True):
    return context.client.delete(url, follow_redirects=follow_redirects, environ_base={'HTTP_USER_AGENT': u'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'})

@given(u'sbir is running')
def flask_setup(context):
    assert context.client


@given(u'the following users exist')
def create_users(context):
    app = context.app
    with app.app_context():
        security = get_extension(context, 'security')
        assert security
        for row in context.table:
            enc_password = encrypt_password(row['password'])
            security.datastore.create_user(
                email=row['email'],
                password=enc_password,
                display_name=row['display_name'])


@given(u'the following organizations exist')
def create_organizations(context):
    from sbir.model import Organization
    app = context.app
    with app.app_context():
        for row in context.table:
            Organization(title=row['title'], description=row['description']).save()



@when(u"I get the '{resource}' resource")
def get_resource(context, resource=None):
    url = get_url(resource)
    context.page = get(context, url)

@then(u"I should see a link to the '{resource}' resource")
def is_link(context, resource):
    expected_url = get_url(resource)
    doc = Document.from_object(json.loads(context.page.data))
    link = doc.links.get('ep:'+resource, None)
    assert link, 'Resource link not found: %s'% resource
    actual_url = link.url
    assert actual_url, "Resource 'ep:%s' not found in links %s" % (resource, doc.links.keys())
    assert expected_url == actual_url, "actual url [%s] does not match expected url [%s]" % (actual_url, expected_url)

@then(u"I should see {num_links} links for the '{rel_uri}' relation")
def count_links(context, num_links, rel_uri):

    doc = Document.from_object(json.loads(context.page.data))
    link = doc.links.get(rel_uri, None)
    assert link, 'Resource link not found: %s'% rel_uri
    assert num_links == link.

    assert actual_url, "Resource 'ep:%s' not found in links %s" % (resource, doc.links.keys())
    assert expected_url == actual_url, "actual url [%s] does not match expected url [%s]" % (actual_url, expected_url)
