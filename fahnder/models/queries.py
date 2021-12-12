from ..utils import es_client, get_sha
from flask import g

def init(app):
    es = es_client(app)

    if not es.indices.exists('queries'):
        # store queries for completion
        es.indices.create("queries", {
            'mappings': {
                '_source': {'enabled': True },
                'properties': {
                    'query_sha': {'type': 'keyword'},
                    'query': {
                        'type': 'text',
                        'fields': {
                            'suggest': {'type': 'completion'}
                        }
                    },
                }
            }
        })

def store_query(query):
    data = dict(
        query_sha = get_sha(query),
        query = query
    )

    g.es.index(index="queries", id=data['query_sha'], body=data)
    # may already exist
