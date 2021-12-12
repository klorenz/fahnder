"""Store events about what people are interested in.  It is about search
queries and results, they clicked at.

This information can be used to propose queries and suggest results.
"""

from flask import g
from ..utils import get_sha, utcnow, es_client

INTEREST_PROPERTIES = {
    # TODO: update this with data from result
    'event': {'type': 'keyword'},
    'query_sha': {'type': 'keyword'},
    'query': { 'type': 'text'},
    'category': { 'type': 'keyword'},
    'engine': { 'type': 'keyword'},
    'type': { 'type': 'keyword'},
    'url': {'type': 'text'},
    'page': {'type': 'integer'},
    'before': {'type': 'date'},
    'after': {'type': 'date'},
    'timestamp': {'type': 'date'},
}

def init(app) -> None:
    es = es_client(app)
    if not es.indices.exists('interests'):
        # store interests of users, i.e. a click event on an entry
        es.indices.create("interests", {
            'mappings': {
                '_source': {'enabled': True },
                'properties': INTEREST_PROPERTIES,
            }
        })

def store_interest(event: str, data: dict) -> None:
    data = data.copy()
    data['query_sha'] = get_sha(data['query'])
    data['timestamp'] = utcnow().isoformat()
    data['event'] = event

    for k in list(data.keys()):
        if k not in INTEREST_PROPERTIES:
            del data[k]

    # register search event
    g.es.index(index="interests", body=data)
