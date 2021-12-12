from ..utils import es_client

def init(app):
    es = es_client(app)

    if not es.indices.exists('docs'):
        # store documents, which can be searched
        es.indices.create("docs", {
            'mappings': {
                '_source': { 'enabled': True },
                'properties': {
                    'title': {
                        'type': 'text', 
                        'fields': {
                            'suggest': { 'type': 'completion' }
                        },
                    },
                    'topic': { 'type': 'text' },
                    'labels': { 'type': 'text',
                        'fields': {
                            'keyword': {'type': 'keyword'}
                        }
                    },
                    'url': { 'type': 'text' },
                    'last_modified_at': {'type': 'date'},
                    'last_modified_by': {
                        'type': 'text', 
                        'fields': {
                            'keyword': {'type': 'keyword'}
                        } },
                    'indexed_at': {'type': 'date'},
                    'created_at': {'type': 'date'},
                    'created_by': {
                        'type': 'text', 
                        'fields': {
                            'keyword': {'type': 'keyword'}
                        }
                    },
                    'content': { 'type': 'text'},
                    'excerpt': { 'type': 'text'},
                }
            }
        })

