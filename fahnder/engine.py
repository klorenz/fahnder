"""The base for all engines

Here you find the common engine attributes::

    attributes:
        weight: 1
        name: null
        categories:
            - general

"""

import datetime
from .search_request import SearchRequest
from .document import Document
from .auth import BearerAuth, get_auth_info, TokenAuth
from requests.auth import HTTPBasicAuth
from flask import current_app, session
from os import environ
import re
from textwrap import dedent


def page_to_offset(page: int, per_page: int, zero_offset: int = 1) -> int:
    """Calculate offset from ``page`` and ``per_page``

    Args:
        page (int): page number (1 based)
        per_page (int): items per page
        zero_offset (int, optional): Offset from zero, e.g. if your engine 
            starts counting from 0, set this to 0. Defaults to 1.

    Returns:
        int: The offset of items
    """

    return (page-1)*per_page+zero_offset


class Engine:
    weight = 1
    name = None
    categories = ['general']
    auth = None

    # thinkable: page, document, mail, source_code_revision, merge_request
    #    issue, project
    #
    document_type = None

    @property
    def auth_info(self):
        return current_app.config['auths'][self.auth]

    @property
    def requests_auth(self):
        """Return auth object for requests

        Protocol is:
        - if exists <AUTH>_BEARER_TOKEN in app.config, take it
        - if exists <AUTH>_BEARER_TOKEN in environ, take it
        - if exists <AUTH>_BEARER_TOKEN in session, take it
        - if exists <AUTH>_BASIC_USER (and <AUTH>_BASIC_PASSWORD) in app.config, take it
        - if exists <AUTH>_BASIC_USER (and <AUTH>_BASIC_PASSWORD) in environ, take it
        - if exists <AUTH>_BASIC_USER in session (and <AUTH>_BASIC_PASSWORD), take it

        Returns:
            requests.auth.AuthBase: An auth object to pass to requests calls
        """
        if self.auth is None:
            return None

        config = current_app.config

        auth = get_auth_info(self.auth)

        if auth.type == 'oauth':
            for prefix in (self.auth, self.auth.upper()):
                token_config_name = f'{prefix}_BEARER_TOKEN'

                for config_source  in (config, environ, session):
                    if token_config_name in config_source:
                        token = config_source[token_config_name]
                        return TokenAuth(token = token)

        if auth.type == 'token':
            for prefix in (self.auth, self.auth.upper()):
                token_config_name = f'{prefix}_TOKEN'

                for config_source  in (config, environ, session):
                    if token_config_name in config_source:
                        token = config_source[token_config_name]
                        return TokenAuth(
                            token = token,
                            headers = auth.config.get('headers'),
                            )

        if auth.type == 'basic':
            for prefix in (self.auth, self.auth.upper()):
                basic_config_user_name = f'{prefix}_BASIC_USER'
                basic_config_password_name = f'{prefix}_BASIC_PASSWORD'

                for config_source in (config, environ, session):
                    if (
                        basic_config_user_name in config_source and 
                        basic_config_password_name in config_source
                    ):
                        return HTTPBasicAuth(
                            username = config_source[basic_config_user_name], 
                            password = config_source[basic_config_password_name]
                            )

        return None



    def search(self, request: SearchRequest):
        """Find items and return info about them

        Args:
            query (str): [description]
            page (int): Find items for this page
            per_page (int): Find ``per_page`` items
            after (datetime, optional): 
                Find items published after this date. Defaults to None.
            before (datetime, optional): find items published before this date. Defaults to None.

        Returns:
            dict: with following keys:
                - **total** - total count of results
                - **results** - list of dicts with keys as defined per document types
        """
        return []

    def suggest(self, query: str):
        return []

    def answer(self, result):
        """Generate Answer from result"""
        return result

    def sort_results(self, results: list, query: str) -> list:
        results.sort(key = lambda x: len(query)*x['title'].count(query)/len(x['title']))
        return results
