from ..engine import Engine, page_to_offset
from datetime import datetime
from jira import JIRA, JIRAError
from flask import session, current_app, abort
from ..search_request import SearchRequest
from ..results import Results
from ..document import Document
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

class JiraEngine(Engine):
    weight = 2
    name = 'JiraEngine'
    categories = ['general', 'issues']
    document_type = 'issue'
    jql = ""

    def get_client(self):
        auth_info = self.auth_info

        if auth_info.type == 'token':
            jira = JIRA(self.hostname, token_auth=auth_info.token)

        if auth_info.type == 'basic':
            jira = JIRA(self.hostname, basic_auth=(auth_info.username, auth_info.password))

        return jira

    def search(self, request: SearchRequest) -> dict:
        jira = self.get_client()

        offset = page_to_offset(request.page, request.per_page)
        cql = self.cql.format(query=request.query)

        if request.before is not None:
            cql += f" updatedDate < {request.before.isoformat()}"
        if request.after is not None:
            cql += f" updatedDate >= {request.after.isoformat()}"
        
        issues = jira.search_issues(self.jql, startAt=offset, maxResults=request.per_page)

        results = []
        for issue in issues:
            results.append(Document(
                type = 'issue',
                url = issue.permalink(),
                title = f"{issue.key}: {issue.fields.summary}",
                published_at = issue.fields.updated,
                excerpt = None,
                fields = {
                    'reporter': issue.fields.reporter.key,
                    'assignee': issue.fields.assignee.key,
                }
            ))

        results = self.sort_results(results, request.query)

        return Results(
            results = results,
            total = results.total
        )

    def suggest(self, query):
        return []

