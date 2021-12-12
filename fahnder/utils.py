import hashlib
from datetime import datetime, timezone
from elasticsearch import Elasticsearch

def utcnow():
    return datetime.utcnow().replace(tzinfo=timezone.utc)

def get_sha(query):
    return hashlib.sha1(query.encode('utf-8')).hexdigest()

def es_client(app):
    return Elasticsearch(app.config.get('ES_HOSTS', 'localhost:9200').split(','))
