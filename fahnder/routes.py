from flask import Blueprint, redirect, jsonify, request, g, make_response, current_app, session
from .search import search
from .utils import utcnow, get_sha
from .models.interests import store_interest
from .search_request import SearchRequest
from .auth import login_required, handle_authorize

import logging

logger = logging.getLogger('routes')

api_routes = Blueprint('fahnder_routes', __name__)

# TODO: add login required

@api_routes.route('/api/search', methods=['GET', 'POST'])
@login_required
def api_search():
    """Search engines
    ---
    get:
      parameters:
        q:
            description: >
                The query
            type: str
        category:
            description: >
                Engine category to search
            default: "general"
        page:
            description: >
                Page to retrieve
            default: 1
        before:
            description: >
                ISO Date or Date time, after before (<) data has been last
                modified.

                OR a negative number, which is days from now.
            default: null
        after:
            description: >
                ISO Date or Date time, after which (>=) data has been last
                modified.

                OR a negative number, which is days from now.
            default: null
    """

    try:
        # posted JSON data gets priority
        request_data = request.get_json()
        # if there is no data
        if request_data is None:
            request_data = dict(request.values)
        logger.debug("request values: %s" % request_data)
        result = search(SearchRequest(**request_data))
        status = 200
    except Exception as e:
        logger.warning("error in search for ", exc_info=1)
        result = {'error': str(e)}
        status = 400

    return make_response(jsonify(**result), status)



@api_routes.route('/')
def index():
    return redirect('/index.html', code=302)


@api_routes.route('/api/recommended', methods=['GET', 'POST'])
@login_required
def api_recomended():
    """Return recommended results

    E.g. the three top-most clicked results on some query

    Returns:
        [type]: [description]
    """

    query = request.values['q']
    count = request.values.get('count', 3)

    sorted((k,v) in kv.get(query).items(), key = lambda x: x[1])


@api_routes.route('/api/index', methods=['POST'])
@login_required
def api_index():
    """index a document.  replaced, if already exists"""

    url = request.values['url']

    doc_id = get_sha(url)

    doc = dict(
        url = url,
        title = request.values['title'],
        excerpt = request.values.get('excerpt', ''),
        content = request.values.get('content', ''),
        topics = request.values.get('topics', []),
        labels = request.values.get('labels', []),
        created_by = request.values.get('created_by', ''),
        created_at = request.values.get('created_at', ''),
        last_modified_by = request.values.get('last_modified_by', ''),
        last_modified_at = request.values.get('last_modified_at', ''),
        indexed_at = utcnow(),
    )

    res = g.es.index(index='docs', id=doc_id, body=doc)

    if res.get('status') == 409:
        g.es.update(index='docs', id=doc_id, body={'doc': doc})

    return jsonify({'result': 'ok'})


@api_routes.route('/api/found', methods=['POST'])
@login_required
def api_found():
    """Store the interest of a user in interests db
    """
    store_interest('found', request.values)
    return jsonify({'result': 'ok'})


@api_routes.route('/api/auth_info', methods=['GET'])
@login_required
def api_auths():
    """Get information about auths, for logging in.

    Returns a dictionary with keys 'auths' and 'auth'. 'auths' has a list
    of auths and 'auth' is a name out of the list
    
    This is only interesting for authentications, which are not configured
    server-side, but need user interaction.
    """

    result = {
        'auths': {}, 
        'auth': current_app.config['FAHNDER'].get('login', {}).get('auth')
    }

    for auth in current_app.config['auths'].values():
        result['auths'][auth.name] = dict(
            name = auth.name,
            type = auth.type,
            logged_in = auth.logged_in,
            login_url = auth.login_url,
        )

    return jsonify(result)


@api_routes.route('/login/basic/<name>', methods=['POST'])
def login_basic(name):
    data = request.get_json()

    if not request.is_json:
        return jsonify({'error': "Expect JSON data"}), 400

    auth_info = current_app.config['auths'][name]
    return handle_authorize(auth_info, None, None)
    result = auth_info.login(data['username'], data['password'])

    logger.debug("basic login result: %r", result)

    return jsonify(result)


@api_routes.route('/login/token/<name>', methods=['POST'])
def login_token(name):
    if not request.is_json:
        return jsonify({'error': "Expect JSON data"}), 400

    auth_info = current_app.config['auths'][name]
    result = auth_info.login(
        request.values['token'],
    )

    return handle_authorize(auth_info, None, None)

    logger.debug("token login result: %r", result)

    return jsonify(result)


@api_routes.route('/logout', methods=['POST', 'GET'])
@login_required
def logout(name):
    session.clear()
    return redirect(f"{current_app.config['FRONTEND_URL']}/")


@api_routes.route('/logout/<name>', methods=['POST', 'GET'])
@login_required
def logout_auth(name):
    for key in list(session.keys()):
        if key.startswith(f"{name}_"):
            session.pop(key)
    return redirect(f"{current_app.config['FRONTEND_URL']}/")

# @auth_routes.route('/logout/<name>')
# def logout(name):
#     session.pop(f'{name}_user', None)
#     return redirect('/')
