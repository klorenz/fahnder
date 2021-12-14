"""Engine to interact with Confluence search API

You can instantiate a confluence class as follows

.. code-block:: yaml

  engines:

    - module: fahnder.engines.confluence
      name: Confluence Title Search
      class: ConfluenceEngine
      categories:
        - general

      attributes:
        # weight of the engine
        weight: 2
        # auth to use
        auth: jira
        server: https://confluence.example.com
        document_type: page
        cql: title ~ "{query}"


Bearer token can be passed in following ways:

"""
from ..engine import Engine, page_to_offset
from ..document import Document
from ..results import Results
from ..search_request import SearchRequest

import re
import requests
from dateutil.parser import parse as dt_parse
import logging
from urllib.parse import urlencode
from ..auth import BearerAuth
from datetime import datetime
from os import environ
import logging

logger = logging.getLogger('engines.confluence')

class ConfluenceEngine(Engine):
    """Engine to do CQL searches on Confluence

    Supports only basic auth and (Bearer) token auth by now.
    
    """
    auth = 'confluence'

    query_terms = False
    term_query = None
    term_operand = 'AND'

    def sort_results(self, results: list, query: str) -> list:
        results.sort(key = lambda x: len(query)*x['title'].count(query)/len(x['title']))
        return results

    def is_valid_term(self, term):
        return re.search(r'^\w[\w\-]*$', term)

    def search(self, request: SearchRequest):
        logger.info("search request: %r", request)

        offset = page_to_offset(request.page, request.per_page)

        if self.term_query is not None:
            terms = request.query.strip().split()

            term_cql = f" {self.term_operand} ".join([
                "("+self.term_query.format(term=term)+")" for term in terms
                if self.is_valid_term(term)
                ])
        else:
            term_cql = ""

        cql = self.cql.format(query=request.query, term_query=term_cql)

        if request.before is not None:
            cql = f"({cql}) and lastModified < {request.before.isoformat()}"
        if request.after is not None:
            cql = f"({cql}) and lastModified >= {request.after.isoformat()}"
        
        response = requests.get("https://wiki.moduleworks.com/rest/api/search", params={
            'cql': "("+cql+")",
            'start': offset,
            'limit': request.per_page,
        }, auth = self.requests_auth(request))

        if not response.ok:
            raise response.raise_for_status()

        results = []
        result = response.json()

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
