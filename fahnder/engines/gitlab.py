"""This engine uses gitlab search api to find pages in a gitlab
instance.

https://docs.gitlab.com/ee/api/search.html#scope-merge_requests
"""

from ..engine import Engine
from ..document import Document
from os import environ

global_bearer_token = None

@blueprint


def setup(app):
    global global_bearer_token
    global_bearer_token = environ.get('GITLAB_ACCESS_TOKEN')


