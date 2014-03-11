from flask.ext.testing import TestCase
import sbir.model as model
from dougrain import Builder, Document
from mongoengine import DoesNotExist
import random, json

__author__ = 'dwcaraway'
__credits__ = 'Dave Caraway'

import logging, sys
logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

log = logging.getLogger(__name__)

MONGO_DATABASE = 'pod_tests_' + str(random.randint(2000, 5000))


class TestConfig(object):
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
    SECURITY_PASSWORD_HASH = 'plaintext'
    SECURITY_REGISTERABLE = True
    SECURITY_CHANGEABLE = True
    SECURITY_RECOVERABLE = True


class BaseTestMixin(TestCase):
    maxDiff = None

    def create_app(self):
        from sbir import create_app
        return create_app(TestConfig)

    def setUp(self):
        pass

    def tearDown(self):
        model.db.connection.drop_database(MONGO_DATABASE)


class RootTest(BaseTestMixin):
    def test_links_to_endpoints(self):
        """
        Verify that root links to the available endpoints
        """
        b = Builder('http://localhost/').add_curie(name='ep', href='/rel/{rel}')\
            .add_link('ep:user', target='/users')\
            .add_link('ep:dataset', target='/datasets')\
            .add_link('ep:organization', target='/organizations')\
            .add_link('ep:schema', target='/schema')
        expected = b.as_object()

        response = self.client.get("/")
        Document.from_object(json.loads(response.data))

        self.assertEquals(response.json, expected)


class DatasetTest(BaseTestMixin):

    # def setUp(self):
    #     super(BaseTestMixin, self).setUp()

    def test_list_datasets(self):
        """
        Verify that all datasets can be retrieved
        """
        data = populate_db(num_datasets=2)  # Create canned data, assign to 'data' property

        expected = ['/datasets/%s' % dataset.id for dataset in data['datasets']]

        response = self.client.get("/datasets")
        response_doc = Document.from_object(response.json)

        hrefs = [link.url() for link in response_doc.links['/rel/dataset']]

        self.assertEquals(set(expected)-set(hrefs), set())

    def test_list_datasets_paginates(self):
        """
        Verify that datasets can be retrieved via pagination
        """
        data = populate_db(num_datasets=100)  # Create canned data

        expected = ['/datasets/%s' % dataset.id for dataset in data['datasets']]
        assert len(expected) is 100

        response = self.client.get("/datasets")
        response_doc = Document.from_object(response.json)
        hrefs = [link.url() for link in response_doc.links['/rel/dataset']]

        while 'next' in response_doc.links.keys():
            response = self.client.get(response_doc.links['next'].url())
            response_doc = Document.from_object(response.json)
            hrefs.extend([link.url() for link in response_doc.links['/rel/dataset']])

        self.assertEquals(set(expected)-set(hrefs), set())

    def test_list_datasets_references_self(self):
        """
        Verify that when we list datasets and paginate over them, that we by default store a
        url reference to self - the EXACT url used to access the dataset
        """
        data = populate_db(num_datasets=50)  # Create canned data

        # Start at /datasets
        response = self.client.get("/datasets")
        response_doc = Document.from_object(response.json)

        # Select the next list of results
        next_url = response_doc.links['next'].url()

        response = self.client.get(next_url)
        response_doc = Document.from_object(response.json)

        # We expect that 'next' link in the first results should equal 'self' link in next list of results
        self.assertEquals(response_doc.links['self'].url(), 'http://localhost%s' % next_url)


    def test_create_dataset(self):
        """
        Verify that a POST to /datasets will create a new dataset
        """
        data = populate_db()
        org = data['orgs'][0].id
        creator = data['users'][0].id


        response = self.client.post('/datasets', data=json.dumps({
                'organization': str(org),
                'created_by': str(creator),
                'title':'footest'
            }), content_type='application/json',
            environ_base={
                'HTTP_USER_AGENT': 'Chrome',
                'REMOTE_ADDR': '127.0.0.1'
            })

        self.assertEquals(201, response.status_code)
        self.assertIsNotNone(response.headers['Location'])

        #Verify the Location is valid by getting it and comparing to expected
        response = self.client.get(response.headers['Location'])
        response_doc = Document.from_object(response.json)

        self.assertEquals('footest', response_doc.properties['title'])

    def test_get_dataset(self):
        """
        Verify ability to GET an individual dataset
        """
        data = populate_db(num_datasets=5)

        test_data = data['datasets'][0]

        response = self.client.get("/datasets/%s" % test_data.id)
        response_doc = Document.from_object(response.json)

        self.assertEquals(test_data.title, response_doc.properties['title'])

        self.assertEquals(200, response.status_code)

    def test_update_dataset(self):
        """
        Verify ability to PUT an individual dataset
        """
        data = populate_db(num_datasets=5)

        test_data = data['datasets'][0]

        request_body = dict(
            organization=str(test_data.organization.id),
            created_by=str(test_data.created_by.id),
            title='test_update_dataset_title'
            )

        response = self.client.put('/datasets/%s' % test_data.id, data=json.dumps(request_body), content_type='application/json',
            environ_base={
                'HTTP_USER_AGENT': 'Chrome',
                'REMOTE_ADDR': '127.0.0.1'
            })

        test_data = model.Dataset.objects.get_or_404(id=test_data.id)

        #Verify that the update happened
        self.assertEquals(200, response.status_code)
        self.assertEquals(request_body['title'], test_data.title)

    def test_delete_dataset(self):
        """
        Verify ability to DELETE a dataset
        """
        data = populate_db(num_datasets=1)

        test_data = data['datasets'][0]

        def query_for_testdata():
            return model.Dataset.objects.get(id=test_data.id)

        #verify that we initially get a result from the db
        self.assertIsNotNone(query_for_testdata())

        response = self.client.delete('/datasets/%s' % test_data.id)

        self.assertEquals(200, response.status_code)

        #Now we get an error raised because document was deleted
        self.assertRaises(DoesNotExist, query_for_testdata)

class UserTest(BaseTestMixin):

    # def setUp(self):
    #     super(BaseTestMixin, self).setUp()

    def test_list_users(self):
        """
        Verify that all users can be retrieved
        """
        data = populate_db(num_users=5, num_datasets=0)  # Create canned data, assign to 'data' property

        expected = ['/users/%s' % user.id for user in data['users']]

        response = self.client.get("/users")
        response_doc = Document.from_object(response.json)

        hrefs = [link.url() for link in response_doc.links['/rel/user']]

        self.assertEquals(set(expected)-set(hrefs), set())

    def test_list_users_paginates(self):
        """
        Verify that user can be retrieved via pagination
        """
        data = populate_db(num_users=100, num_datasets=0)  # Create canned data

        expected = ['/users/%s' % user.id for user in data['users']]
        assert len(expected) is 100

        response = self.client.get("/users")
        response_doc = Document.from_object(response.json)
        hrefs = [link.url() for link in response_doc.links['/rel/user']]

        while 'next' in response_doc.links.keys():
            response = self.client.get(response_doc.links['next'].url())
            response_doc = Document.from_object(response.json)
            hrefs.extend([link.url() for link in response_doc.links['/rel/user']])

        self.assertEquals(set(expected)-set(hrefs), set())

    def test_create_user(self):
        """
        Verify that a POST to /users will create a new user
        """
        response = self.client.post('/users', data=json.dumps({
                'display_name': 'jim',
                'email': 'jim@test.com',
                'password':'password'
            }), content_type='application/json',
            environ_base={
                'HTTP_USER_AGENT': 'Chrome',
                'REMOTE_ADDR': '127.0.0.1'
            })

        self.assertEquals(201, response.status_code)
        self.assertIsNotNone(response.headers['Location'])

        #Verify the Location is valid by getting it and comparing to expected
        response = self.client.get(response.headers['Location'])
        response_doc = Document.from_object(response.json)

        self.assertEquals('jim@test.com', response_doc.properties['email'])

    def test_get_user(self):
        """
        Verify ability to GET an individual user
        """
        data = populate_db(num_users=100)

        test_data = data['users'][0]

        response = self.client.get("/users/%s" % test_data.id)
        response_doc = Document.from_object(response.json)

        self.assertEquals(test_data.email, response_doc.properties['email'])

        self.assertEquals(200, response.status_code)

    def test_update_user(self):
        """
        Verify ability to PUT an individual user
        """
        data = populate_db(num_users=5)

        test_data = data['users'][0]

        request_body = dict(
            display_name='updated_display',
            email='updated@email.com',
            password='password'
            )

        response = self.client.put('/users/%s' % test_data.id, data=json.dumps(request_body), content_type='application/json',
            environ_base={
                'HTTP_USER_AGENT': 'Chrome',
                'REMOTE_ADDR': '127.0.0.1'
            })

        test_data = model.User.objects.get_or_404(id=test_data.id)

        #Verify that the update happened
        self.assertEquals(200, response.status_code)
        self.assertEquals(request_body['display_name'], test_data.display_name)

    def test_delete_user(self):
        """
        Verify ability to DELETE a user
        """
        data = populate_db(num_users=10)

        test_data = data['users'][0]

        def query_for_testdata():
            return model.User.objects.get(id=test_data.id)

        #verify that we initially get a result from the db
        self.assertIsNotNone(query_for_testdata())

        response = self.client.delete('/users/%s' % test_data.id)

        self.assertEquals(200, response.status_code)

        #Now we get an error raised because document was deleted
        self.assertRaises(DoesNotExist, query_for_testdata)

class OrganizationTest(BaseTestMixin):

    # def setUp(self):
    #     super(BaseTestMixin, self).setUp()

    def test_list_organizations(self):
        """
        Verify that organizations can be retrieved
        """
        data = populate_db(num_orgs=5, num_datasets=0)  # Create canned data, assign to 'data' property

        expected = ['/organizations/%s' % org.id for org in data['orgs']]

        response = self.client.get("/organizations")
        response_doc = Document.from_object(response.json)

        hrefs = [link.url() for link in response_doc.links['/rel/organization']]

        print hrefs

        self.assertEquals(set(expected)-set(hrefs), set())

    def test_list_organizations_paginates(self):
        """
        Verify that organizations can be retrieved via pagination
        """
        data = populate_db(num_orgs=100, num_datasets=0)  # Create canned data

        expected = ['/organizations/%s' % org.id for org in data['orgs']]
        assert len(expected) is 100

        response = self.client.get("/organizations")
        response_doc = Document.from_object(response.json)
        hrefs = [link.url() for link in response_doc.links['/rel/organization']]

        while 'next' in response_doc.links.keys():
            response = self.client.get(response_doc.links['next'].url())
            response_doc = Document.from_object(response.json)
            hrefs.extend([link.url() for link in response_doc.links['/rel/organization']])

        self.assertEquals(set(expected)-set(hrefs), set())

    def test_create_organization(self):
        """
        Verify that a POST to /organizations will create a new organization
        """
        response = self.client.post('/organizations', data=json.dumps({
                'title': 'testorg'
            }), content_type='application/json',
            environ_base={
                'HTTP_USER_AGENT': 'Chrome',
                'REMOTE_ADDR': '127.0.0.1'
            })

        self.assertEquals(201, response.status_code)
        self.assertIsNotNone(response.headers['Location'])

        #Verify the Location is valid by getting it and comparing to expected
        response = self.client.get(response.headers['Location'])
        response_doc = Document.from_object(response.json)

        self.assertEquals('testorg', response_doc.properties['title'])

    def test_get_organization(self):
        """
        Verify ability to GET an individual organization
        """
        data = populate_db(num_orgs=100)

        test_data = data['orgs'][0]

        response = self.client.get("/organizations/%s" % test_data.id)
        response_doc = Document.from_object(response.json)

        self.assertEquals(test_data.title, response_doc.properties['title'])

        self.assertEquals(200, response.status_code)

    def test_update_organization(self):
        """
        Verify ability to PUT an individual organization
        """
        data = populate_db(num_orgs=5)

        test_data = data['orgs'][0]

        request_body = dict(
            title='updated_title'
            )

        response = self.client.put('/organizations/%s' % test_data.id, data=json.dumps(request_body), content_type='application/json',
            environ_base={
                'HTTP_USER_AGENT': 'Chrome',
                'REMOTE_ADDR': '127.0.0.1'
            })

        test_data = model.Organization.objects.get_or_404(id=test_data.id)

        #Verify that the update happened
        self.assertEquals(200, response.status_code)
        self.assertEquals(request_body['title'], test_data.title)

    def test_delete_organization(self):
        """
        Verify ability to DELETE an organization
        """
        data = populate_db(num_orgs=10)

        test_data = data['orgs'][0]

        def query_for_testdata():
            return model.Organization.objects.get(id=test_data.id)

        #verify that we initially get a result from the db
        self.assertIsNotNone(query_for_testdata())

        response = self.client.delete('/organizations/%s' % test_data.id)

        self.assertEquals(200, response.status_code)

        #Now we get an error raised because document was deleted
        self.assertRaises(DoesNotExist, query_for_testdata)



def populate_db(num_users=1, num_orgs=1, num_datasets=0):
    """
    Populate the database with canned data
    """
    users = [model.User(password='pass', email='test%s@test.com'%x, display_name='testuser%s'%x) for x in range(num_users)]
    users = model.User.objects.insert(users)

    orgs = [model.Organization(title='org%s'%x) for x in range(num_orgs)]
    orgs = model.Organization.objects.insert(orgs)

    data = dict(users=users, orgs=orgs)

    if num_datasets:
        datasets = [model.Dataset(title='Dataset%d'% x, organization=orgs[0], created_by=users[0]) for x in range(num_datasets)]

        data['datasets']=model.Dataset.objects.insert(datasets)

    return data


