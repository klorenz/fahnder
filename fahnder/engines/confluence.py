"""Engine to interact with Confluence search API

You can instantiate a confluence class as follows:

engines:
    - name: my cool confluence search engine
      attributes:
        cql: 'title ~ {query}'

Bearer token can be passed in following ways:

- global: from CONFLUENCE_BEARER_TOKEN var, useful for development
- via header: X-FAHNDER-CONFLUENCE-BEARER-TOKEN

"""
from ..engine import Engine, page_to_offset
from ..document import Document
from ..results import Results
from ..search_request import SearchRequest

import requests
from dateutil.parser import parse as dt_parse
import logging
from urllib.parse import urlencode
from ..auth import BearerAuth
from datetime import datetime
from os import environ

# the bearer token unless 
global_bearer_token = None

def setup(app):
    global global_bearer_token
    global_bearer_token = environ.get('CONFLUENCE_BEARER_TOKEN')

    # setup oauth here

class ConfluenceEngine(Engine):
    auth = 'confluence'

    def sort_results(self, results: list, query: str) -> list:
        results.sort(key = lambda x: len(query)*x['title'].count(query)/len(x['title']))
        return results

    def search(self, request: SearchRequest):
        self.logger.info(
            "search: query=%s, page=%s, per_page=%s, before=%s, after=%s", 
            query, page, per_page, before, after)

        offset = page_to_offset(request.page, request.per_page)
        cql = self.cql.format(query=request.query)

        if request.before is not None:
            cql += f" lastModified < {request.before.isoformat()}"
        if request.after is not None:
            cql += f" lastModified >= {request.after.isoformat()}"

        
        response = requests.get("https://wiki.moduleworks.com/rest/api/search", params={
            'cql': "("+cql+")",
            'start': offset,
            'limit': request.per_page,
        }, auth = self.requests_auth)

        print(response.url)

        print(response)

        results = []
        result = response.json()
        print(result)

        for item in result['results']:
            results.append(Document(
                type = 'page',
                url = result['_links']['base'] + item['url'],
                title = item['title'].replace('@@@hl@@@', '').replace('@@@endhl@@@', ''),
                published_at = dt_parse(item['lastModified']),
                excerpt = item['excerpt'].replace('@@@hl@@@', '').replace('@@@endhl@@@', '')
            ))

        results = self.sort_results(results, request.query)

        return Results(
            results = results,
            total = result['totalSize'],
        )


    def suggest(self, query, count=100):
        results = self.search(query, page=1, per_page=count)

        for result in results:
            result['suggestion'] = result['title']
            del result['content']

        return results


class ConfluenceSpaceSearch(ConfluenceEngine):
    weight = 3
    name = 'ConfluenceSpace'
    categories = ['general']

    def search(self, query: str, page: int, per_page: int, before: datetime = None, after=None):
        return []

    def suggest(self, query):
        return []


class ConfluenceTitleSearch(ConfluenceEngine):
    weight = 2
    name = 'ConfluenceTitle'
    categories = ['general']
    document_type = 'page'
    cql = 'title ~ {query} AND type = page'

class ConfluenceMainSpaceSearch(ConfluenceEngine):
    weight = 5
    name = 'ConfluenceMainSpace'
    categories = ['general']
    document_type = 'page'
    cql = 'title ~ {query} AND space = MYSPACE AND type = page'

class ConfluenceBlogSearch(ConfluenceEngine):
    weight = 3
    name = 'ConfluenceBlog'
    categories = ['general', 'news']
    document_type = 'page'
    cql = 'title ~ {query} AND type = blogpost'
