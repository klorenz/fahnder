import requests
from textwrap import dedent
from importlib import import_module
import logging

# OAUTH2 implementation from https://github.com/ityoung/gitlab-oauth-example/blob/master/main.py

from flask import Flask, redirect, url_for, session, jsonify, make_response, request, g, abort, current_app
from authlib.integrations.flask_client import OAuth
from loginpass import create_flask_blueprint
from werkzeug.exceptions import HTTPException, Unauthorized
from werkzeug.datastructures import WWWAuthenticate
import requests
from os import environ
from collections import namedtuple
import sys

from flask import current_app, g

from functools import wraps, partial


def handle_authorize(remote, token, user_info):
    logger.debug("handle_authorize remote=%r token=%r user_info=%r", remote, token, user_info)
    # if token and user_info are none, loginpass could not handle
    # authorization. In this case check if 
    if token is None:
        data = request.get_json()
        logger.debug("handle_authorize data=%r", data)
        if 'token' in data:
            session[f"{remote.name}_TOKEN"] = data['token']

        else:
            session[f"{remote.name}_BASIC_USER"] = data['username']
            session[f"{remote.name}_BASIC_PASSWORD"] = data['password']
        # fetch user info from given URL, if possible

    else:
        session[f"{remote.name}_BEARER_TOKEN"] = token

    if user_info is not None:
        session[f"{remote.name}_USER_INFO"] = user_info

    logger.debug("handle_authorize session=%r", session)

    return redirect(f"{current_app.config['FRONTEND_URL']}/")

logger = logging.getLogger('auth')

class AuthInfo:
    def __init__(self, config, backend=None):
        assert config['type'] in ('basic', 'oauth')
        self.type = config['type']
        self.name = config['name']
        self.config = config
        self.backend = backend

    @property
    def logged_in(self):
        logger.debug("session: %r", session)
        if self.type == 'oauth':
            return f'{self.name}_BEARER_TOKEN' in session
        elif self.type == 'basic':
            return (
                f'{self.name}_BASIC_USER' in session and
                f'{self.name}_BASIC_PASSWORD' in session
            )

    @property
    def login_route(self):
        if self.type == 'oauth':
            return f"/login/{self.name}"
        else:
            return f"/login/basic/{self.name}"

    @property
    def login_url(self):
        if 'login_url' in self.config:
            return self.config['login_url']

    def login(self, *args, **kwargs):
        """Passes all arguments to underlying backend's login method.

        Returns:
            dict: User information:

                sub -> ID
                name
                email
                preferred_username
                profile URL
                picture URL
                website URL
        """
        user_info = self.backend.login(*args, **kwargs)
        handle_authorize(self, None, user_info)
        return user_info

def get_auth_info(name) -> AuthInfo:
    """Return AuthInfo Object

    Args:
        name (str): Name of auth_info to get

    Returns:
        AuthInfo: auth_info object
    """
    return current_app.config['auths'][name]


# simple bearer authentication for requests
class BearerAuth(requests.auth.AuthBase):

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers["authorization"] = "Bearer " + self.token
        return r

class TokenAuth(requests.auth.AuthBase):

    def __init__(self, token, headers = {"authorization": "Bearer {token}"}, values=None):
        self.token = token
        self.headers = headers
        self.values = values or {}

    def __call__(self, r):
        for k,v in self.headers.items():
            r.headers[k] = v.format(token=self.token, **values)

        return r

# bearer authentication in OAuth2 context
class BearerAuthenticate(WWWAuthenticate):
    # see https://tools.ietf.org/id/draft-ietf-oauth-v2-bearer-22.xml
    INVALID_REQUEST = 'invalid_request'
    INVALID_TOKEN = 'invalid_token'
    INSUFFICIENT_SCOPE = 'insufficient_scope'

    scope = WWWAuthenticate.auth_property('scope')
    error = WWWAuthenticate.auth_property('error')
    error_description = WWWAuthenticate.auth_property('error_description')


# def handle_authorize(remote, token, user_info):
#     """Handle authorize

#     This function is called from OAuth class from authlib.

#     Token is a dictionary with keys `access_token`, `token_type` (typically
#     'Bearer'), `refresh_token`, `scope` ('read_user') and `created_at`.

#     `user_info` is a dictionary with keys `sub`, `name`, `email`, 
#     `preferred_username` (which is the username), `profile` (a link to profile),
#     `picture`, `website`.

#     Args:
#         remote ([type]): [description]
#         token ([type]): [description]
#         user_info ([type]): [description]
#     """

#     session['user_info'] = user_info
#     return jsonify(user_info)

def handle_bearer_authorize(remote, bearer_token, user_info):
    session['user_info'] = user_info

def verify_login(handle_bearer_authorize = lambda token, user_info: None):
    # handled already by OAuth module
    if 'user_info' in session:
        return True

    if 'authorization' not in request.headers:
        raise Unauthorized(
            www_authenticate=BearerAuthenticate(
                auth_type='Bearer',
                realm = g.oauth_hostname,
            ))

    # Maybe user is using another bearer token
    (auth_type, token) = request.headers['authorization'].split(None, 1)
    if auth_type != 'Bearer':
        raise Unauthorized(www_authenticate=BearerAuthenticate(
            error = BearerAuthenticate.INVALID_REQUEST,
            error_description = "Only Bearer tokens allowed here."
            ))
            
    client = g.oauth_client()
    url = client.OAUTH_CONFIG['api_base_url'] + client.OAUTH_CONFIG['userinfo_endpoint']

    # verify that the Bearer token has been issued by underlying identity provider
    response = requests.get(url, headers = {'authorization': f'Bearer {token}'})

    # TODO: maybe simply copy the headers from response
    if response.status_code != 200:
        raise Unauthorized(www_authenticate=BearerAuthenticate(
            error = BearerAuthenticate.INVALID_REQUEST,
            error_description = response
            ))

    return handle_bearer_authorize(remote = client, token=token, user_info = response.json())


def init_oauth(app,
    oauth_name,

    client_id,
    client_secret,
    hostname = None,
    backends = None,
    handle_authorize = handle_authorize,
    handle_bearer_authorize = handle_bearer_authorize,
    ):
    """Initialize OAuth

    Args:
        app (Flask): flask app
        oauth_name (str): Name of the OAuth provider (must be python identifier)
        client_id (str): client_id 
        client_secret (str): client_secret
        hostname (str, optional): used if no backends given.
        backends (list, optional): List of OAuth backends. If none given, uses
           hostname to connect to gitlab as identity provider.

    Returns:
        function: decorator ``login_required``, which you can use (as innermost 
            decorator) to protect an endpoint
    """

    if backends is None:
        backends = [ create_gitlab_backend(oauth_name, hostname) ]

    oauth = OAuth(app)

    assert oauth_name.isidentifier(), "Name must be a valid python identifier"

    name_upper = oauth_name.upper() 

    app.config[name_upper+'_CLIENT_ID'] = client_id
    app.config[name_upper+'_CLIENT_SECRET'] = client_secret

    sys.stderr.write('config: %s\n' % app.config)

    bp = create_flask_blueprint(backends, oauth, handle_authorize)
    app.register_blueprint(bp, url_prefix='')

    @app.before_request
    def add_oauth_object():
        g.oauth = oauth
        g.oauth_name = oauth_name
        g.oauth_hostname = hostname
        g.oauth_client = lambda: oauth.create_client(oauth_name)

    def login_required(f=None, **kwargs):
        if f is None:
            return partial(login_required, **kwargs)

        @wraps(f)
        def decorator_function(*args, **kwargs):
            verify_login(handle_bearer_authorize=handle_bearer_authorize)
            return f(*args, **kwargs)

        return decorator_function

    return login_required

# see https://github.com/authlib/demo-oauth-client/blob/master/flask-multiple-login/app.py

# from authlib.integrations.flask_client import OAuth

# @blueprint.route('/login/<name>')
# def login(name):
#     cl
#     redirect_url = url_for('auth', name=name, _external=True)

from authlib.integrations.flask_client import OAuth
oauth = OAuth()

# from flask import Blueprint
# auth_routes = Blueprint('auth_routes', __name__)

# @auth_routes.route('/login/<name>')
# def login(name):
#     client = oauth.create_client(name)
#     if not client:
#         abort(404)

#     redirect_uri = url_for('auth', name=name, _external=True)
#     return client.authorize_redirect(redirect_uri)


# @auth_routes.route('/auth/<name>')
# def auth(name):
#     client = oauth.create_client(name)
#     if not client:
#         abort(404)

#     token = client.authorize_access_token()
#     user = token.get('userinfo')
#     if not user:
#         user = client.userinfo()

#     session[f'{name}_user'] = user
#     return redirect('/')


# @auth_routes.route('/logout/<name>')
# def logout(name):
#     session.pop(f'{name}_user', None)
#     return redirect('/')

# @auth_routes.route('/logout')
# def logout_all():
#     for name in current_app.config['oauth_clients']:
#         session.pop(f'{name}_user', None)
#         session.pop(f'{name}_user', None)
#         return redirect('/')
    
#     # for 
#     return redirect('/')

#def register(app, name, type, **kwargs):



class HttpBasicAuth:
    def __init__(self, authlib_obj, name, **kwargs):
        self.config = kwargs
        self.name = name
        self.authlib_obj = authlib_obj

# work through auths
def init_auths(app, auths):
    oauth.init_app(app)

    backends = []
    code = ''
    app.config['auths'] = {}
    for auth in auths:
        backend = None

        module = import_module(auth['module'])

        if auth['type'] == 'oauth':
            name_upper = auth['name'].upper()
            client_id_name = name_upper+'_CLIENT_ID'
            client_secret_name = name_upper+'_CLIENT_SECRET'

            if client_id_name in environ:
                app.config[client_id_name] = environ[client_id_name]
            if client_secret_name in environ:
                app.config[client_secret_name] = environ[client_secret_name]

        if 'factory' in auth:
            factory_name = list(auth['factory'].keys())[0]
            factory = getattr(module, factory_name)
            kwargs = {'name': auth['name']}
            kwargs.update(auth['factory'][factory_name])
            backend = factory(**kwargs)

        if auth['type'] == 'oauth':
            if 'backend' in auth:
                backend_class = getattr(module, auth['backend'])
                backends.append(backend_class)
            else:
                backends.append(backend)


        app.config['auths'][auth['name']] = AuthInfo(auth, backend)

    exec(code, dict(backends = backends))
    blueprint = create_flask_blueprint(backends, oauth, handle_authorize=handle_authorize)
    app.register_blueprint(blueprint)
