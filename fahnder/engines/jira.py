from ..engine import Engine
from datetime import datetime
from jira import JIRA, JIRAError
from flask import session, current_app, abort

class JiraBasicAuth():
    def __init__(self, name, url):
        self.name = name
        self.url = url

    def login(self, username: str, password: str) -> dict:
        """Login to Jira and return a user_info dict

        Args:
            username (str): the username
            password (str): the passowrd

        Returns:
            dict:
                a dictionary with information about currently
                logged in Usr
        """
        session[f'{self.name}_BASIC_USER'] = username
        session[f'{self.name}_BASIC_PASSWORD'] = password
        try:
            user_info = JIRA(self.url, basic_auth=(username, password)).user(username).raw
        except JIRAError as e:
            if e.status_code == 401:
                abort(e.status_code, "Bad Credentials")
            abort(e.status_code, e.text)

        return dict(
            sub = user_info['key'],
            name = user_info['displayName'],
            email = user_info['emailAddress'],
            preferred_username = username,
            profile_url = f"{self.url}/secure/ViewProfile.jspa?name={user_info['key']}",
            picture_url = user_info['avatarUrls']['48x48'],
            website_url = None,
        )

class JiraSummarySearch(Engine):
    weight = 2
    name = 'JiraSummary'
    categories = ['general', 'issues']
    document_type = 'issue'

    def get_client(self):
        if self.auth is not None:
            auth = current_app.config['auths'][self.auth]

        if auth.type == 'token':
            jira = JIRA(self.hostname, token_auth=auth.token)

        if auth.type == 'basic':
            jira = JIRA(self.hostname, basic_auth=(auth.username, auth.password))

        return jira

    def search(self, query: str, page: int, per_page: int, before: datetime = None, after: datetime = None) -> dict:

        # if auth.type == 'oauth':
        # see: https://jira.readthedocs.io/examples.html#oauth
        #     jira = JIRA(basic_auth=(

        return []

    def suggest(self, query):
        return []


class JiraTextSearch(Engine):
    weight = 2
    name = 'JiraText'
    categories = ['general', 'issues']
    document_type = 'issue'

    def search(self, query: str, page: int, per_page: int, before: datetime = None, after: datetime = None) -> 'list[dict]':
        return []

    def suggest(self, query):
        return []
