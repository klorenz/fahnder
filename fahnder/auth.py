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

from authlib.integrations.flask_client import OAuth

logger = logging.getLogger('auth')
oauth = OAuth()


def handle_authorize(remote, token, user_info):
    logger.debug("handle_authorize remote=%r token_is_none=%r user_info=%r", remote, token is None, user_info)
    # if token and user_info are none, loginpass could not handle
    # authorization. In this case check if 
    if token is None:
        data = request.get_json()
        auth_info = get_auth_info(remote.name)

        logger.debug("handle_authorize data=%r", data)
        if 'token' in data:
            user_info = auth_info.login(
                request.values['token'],
            )
            session[f"{remote.name}_TOKEN"] = data['token']

        else:
            user_info = auth_info.login(data['username'], data['password'])

            session[f"{remote.name}_BASIC_USER"] = data['username']
            session[f"{remote.name}_BASIC_PASSWORD"] = data['password']
        # fetch user info from given URL, if possible

    else:
        session[f"{remote.name}_BEARER_TOKEN"] = token

    if user_info is not None:
        session[f"{remote.name}_USER_INFO"] = user_info

    logger.debug("handle_authorize session=%r", session)

    return redirect(f"{current_app.config['FRONTEND_URL']}/")


def login_required(func):
    @wraps(func)
    def check_login(*args, **kwargs):
        primary_auth = current_app.config['FAHNDER'].get('auth')
        if primary_auth is not None:
            auth_info = get_auth_info(primary_auth)
            if f"{auth_info.name}_user_info" not in session:
                current_app.view_functions['/login/<name>'](auth_info.name)
                raise Unauthorized()

        return func(*args, **kwargs)
        
    return check_login


class AuthInfo:
    def __init__(self, config, backend=None):
        assert config['type'] in ('basic', 'oauth')
        self.type = config['type']
        self.name = config['name']
        self.config = config
        self.backend = backend

    def is_logged_in(self, session):
        logger.debug("session: %r", session)
        if self.type == 'oauth':
            return f'{self.name}_BEARER_TOKEN' in session
        elif self.type == 'basic':
            return (
                f'{self.name}_BASIC_USER' in session and
                f'{self.name}_BASIC_PASSWORD' in session
            )

    @property
    def logged_in(self):
        # works only in application context
        return self.is_logged_in(session)

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

# # bearer authentication in OAuth2 context
# class BearerAuthenticate(WWWAuthenticate):
#     # see https://tools.ietf.org/id/draft-ietf-oauth-v2-bearer-22.xml
#     INVALID_REQUEST = 'invalid_request'
#     INVALID_TOKEN = 'invalid_token'
#     INSUFFICIENT_SCOPE = 'insufficient_scope'

#     scope = WWWAuthenticate.auth_property('scope')
#     error = WWWAuthenticate.auth_property('error')
#     error_description = WWWAuthenticate.auth_property('error_description')

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
