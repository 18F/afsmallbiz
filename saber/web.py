import json,logging, urlparse
from urllib import urlencode
from flask import jsonify, Response, abort, Blueprint, request, url_for, make_response
from dougrain import Builder, Document
from sbir.model import Dataset, User, Organization, Schema
from mongoengine import NotUniqueError
from bson import ObjectId

__author__ = 'dwcaraway'
__credits__ = ['Dave Caraway']

log = logging.getLogger(__name__)

api = Blueprint('api', __name__)

@api.route('/', methods=['GET'])
def index():
    """
    Handle API home, the starting point, which lists endpoints to navigate to
    """

    #TODO /rel should be found using url_for call

    b = Builder(request.url).add_curie('ep', '/rel/{rel}')\
        .add_link('ep:user', url_for('.list_users'))\
        .add_link('ep:schema', url_for('.list_all_schema'))
    o = b.as_object()

    return Response(json.dumps(o), mimetype='application/json')

# ------------------- DATASETS --------------------------------------

@api.route('/datasets', methods=['GET'])
def list_datasets():
    """
    Lists datasets
    """
    page = int(request.args.get('page', '1'))

    pagination = Dataset.objects.paginate(page=page, per_page=10)
    b = Builder(request.url).add_link('home', url_for('.index'))

    for dataset in pagination.items:
        b.add_link('/rel/dataset', url_for('.get_dataset', id=dataset.id))

    if pagination.has_prev:
        b.add_link('prev', url_for('.list_datasets', page=pagination.prev_num))

    if pagination.has_next:
        b.add_link('next', url_for('.list_datasets', page=pagination.next_num))

    o = b.as_object()

    return Response(json.dumps(o), mimetype='application/json')

@api.route('/datasets', methods=['POST'])
def create_dataset():
    """
    Creates a Dataset
    """
    #TODO require authentication
    #TODO don't have created_by passed in
    #TODO verify that user has authority to create datasets for an organization

    data = request.get_json()

    user = User.objects.get_or_404(id=ObjectId(data['created_by']))
    org = Organization.objects.get_or_404(id=ObjectId(data['organization']))

    dataset = Dataset(
        title=data['title'],
        organization=org,
        created_by=user)
    dataset.save()

    response = Response(headers={'Location': url_for('.get_dataset', id=dataset.id), 'Content-Type':'text/plain'})
    response.status_code = 201

    return response

@api.route('/datasets/<id>', methods=['GET'])
def get_dataset(id):
    """
    Retrieve a Dataset
    """

    #TODO cleanup the garbage in the JSON response (e.g. extra fields, strict date/object references)

    dataset = Dataset.objects.get_or_404(id=ObjectId(id))
    dataset_str = dataset.to_json()

    d = Document.from_object(json.loads(dataset_str))
    d.add_link('self', request.url)
    d.set_curie('ds', '/rel/{rel}')
    d.add_link('home', url_for('.index'))
    d.add_link('ds:datasets', url_for('.list_datasets'))

    # For references, add links
    d.add_link('ds:organization', url_for('.get_org', id=dataset.organization.id))
    d.add_link('ds:created_by', url_for('.get_user', id=dataset.created_by.id))

    return Response(json.dumps(d.as_object()), mimetype='application/json')

@api.route('/datasets/<id>', methods=['PUT'])
def update_dataset(id):
    """
    Update a dataset.
    """
    #TODO check permissions

    dataset = Dataset.objects.get_or_404(id=ObjectId(id))

    request_dict = request.json

    #TODO need to grab all attributes that should be updated
    dataset.title = request_dict['title']
    dataset.save()

    return Response(200, mimetype='text/plain')


@api.route('/datasets/<id>', methods=['DELETE'])
def delete_dataset(id):
    """
    Deletes a dataset.
    """
    #TODO check permissions

    dataset = Dataset.objects.get_or_404(id=ObjectId(id))
    dataset.delete()

    return Response(200, mimetype='text/plain')

# ------------------- USERS --------------------------------------

@api.route('/users', methods=['GET'])
def list_users():
    """
    Lists Users
    """
    #TODO check permissions -- must be admin
    #TODO support queries

    page = int(request.args.get('page', '1'))

    pagination = User.objects.paginate(page=page, per_page=10)

    b = Builder(request.url).add_link('home', url_for('.index'))

    for user in pagination.items:
        b.add_link('/rel/user', url_for('.get_user', id=user.id))

    if pagination.has_prev:
        b.add_link('prev', url_for('.list_users', page=pagination.prev_num))

    if pagination.has_next:
        b.add_link('next', url_for('.list_users', page=pagination.next_num))

    o = b.as_object()

    return Response(json.dumps(o), mimetype='application/json')

@api.route('/users', methods=['POST'])
def create_user():
    """
    Creates a user
    """
    #TODO require authentication -- must be admin
    #TODO verify that user has authority to create datasets for an organization

    data = request.get_json()

    user = User(password=data['password'],
                email=data['email'],
                display_name=data['display_name']
    )

    try:
        user.save()
    except NotUniqueError:
        resp = Response(json.dumps({'error':'That user already exists'}), headers={'Content-Type':'application/json'})
        resp.status_code = 409  #Conflict
        return resp

    response = Response(headers={'Location': url_for('.get_user', id=user.id), 'Content-Type':'text/plain'})
    response.status_code = 201

    return response

@api.route('/users/<id>', methods=['GET'])
def get_user(id):
    """
    Retrieve a User
    """

    #TODO cleanup the garbage in the JSON response (e.g. extra fields, strict date/object references)

    user = User.objects.get_or_404(id=ObjectId(id))
    user_str = user.to_json()

    d = Document.from_object(json.loads(user_str))
    d.add_link('self', request.url)
    d.set_curie('us', '/rel/{rel}')
    d.add_link('home', url_for('.index'))
    d.add_link('us:users', url_for('.list_users'))

    return Response(json.dumps(d.as_object()), mimetype='application/json')

@api.route('/users/<id>', methods=['PUT'])
def update_user(id):
    """
    Update a user.
    """
    #TODO check permissions

    user = User.objects.get_or_404(id=ObjectId(id))

    request_dict = request.json

    #TODO need to grab all attributes that should be updated
    user.email = request_dict['email']
    user.display_name = request_dict['display_name']
    user.password = request_dict['password']
    user.save()

    return Response(200, mimetype='text/plain')


@api.route('/users/<id>', methods=['DELETE'])
def delete_user(id):
    """
    Deletes a user.
    """
    #TODO check permissions

    user = User.objects.get_or_404(id=ObjectId(id))
    user.delete()

    return Response(200, mimetype='text/plain')


# ------------------- ORGANIZATIONS --------------------------------------

@api.route('/organizations', methods=['GET'])
def list_orgs():
    """
    Lists Organizations
    """
    #TODO check permissions
    #TODO support queries

    page = int(request.args.get('page', '1'))

    pagination = Organization.objects.paginate(page=page, per_page=10)

    b = Builder(request.url).add_link('home', url_for('.index'))

    for user in pagination.items:
        b.add_link('/rel/organization', url_for('.get_org', id=user.id))

    if pagination.has_prev:
        b.add_link('prev', url_for('.list_orgs', page=pagination.prev_num))

    if pagination.has_next:
        b.add_link('next', url_for('.list_orgs', page=pagination.next_num))

    o = b.as_object()

    return Response(json.dumps(o), mimetype='application/json')

@api.route('/organizations', methods=['POST'])
def create_org():
    """
    Creates an organization
    """
    #TODO require authentication -- must be admin
    #TODO verify that user has authority to create datasets for an organization

    data = request.get_json()

    org = Organization(title=data['title'])
    org.save()

    response = Response(headers={'Location': url_for('.get_org', id=org.id), 'Content-Type':'text/plain'})
    response.status_code = 201

    return response

@api.route('/organizations/<id>', methods=['GET'])
def get_org(id):
    """
    Retrieve an organization
    """

    #TODO cleanup the garbage in the JSON response (e.g. extra fields, strict date/object references)

    org = Organization.objects.get_or_404(id=ObjectId(id))
    org_str = org.to_json()

    d = Document.from_object(json.loads(org_str))
    d.add_link('self', request.url)
    d.set_curie('og', '/rel/{rel}')
    d.add_link('home', url_for('.index'))
    d.add_link('og:organization', url_for('.list_orgs'))

    return Response(json.dumps(d.as_object()), mimetype='application/json')

@api.route('/organizations/<id>', methods=['PUT'])
def update_org(id):
    """
    Update an organization.
    """
    #TODO check permissions

    org = Organization.objects.get_or_404(id=ObjectId(id))

    request_dict = request.json

    #TODO need to grab all attributes that should be updated
    org.title = request_dict['title']
    org.save()

    return Response(200, mimetype='text/plain')

@api.route('/organizations/<id>', methods=['DELETE'])
def delete_org(id):
    """
    Deletes an organization.
    """
    #TODO check permissions
    #TODO reassign all datasets of organization to another organization

    org = Organization.objects.get_or_404(id=ObjectId(id))
    org.delete()

    return Response(200, mimetype='text/plain')

# ------------------- SCHEMA --------------------------------------

@api.route('/schema', methods=['GET'])
def list_all_schema(page=1):
    """
    Handle routing of JSON schema (see json-schema.org)
    """
    ret = Schema.objects.paginate(page=page, per_page=10)
    return jsonify(ret)

@api.route('/schema', methods=['POST'])
def create_schema():
    """
    Creates a schema
    """
    schema = Schema()
    schema.save()
    b = Builder(request.url).add_link('/rel/schema', '/schema/%d' % schema.id)

    #TODO implement
    return abort(501)


@api.route('/schema/{id}', methods=['GET'])
def get_schema(id=None):
    """
    Handle routing of JSON schema (see json-schema.org)
    """
    ret = Schema.objects.get_or_404(_id=id)
    return jsonify(ret)

