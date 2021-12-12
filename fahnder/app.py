from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException
from flask_cors import CORS
from .config import Config, is_true
from .auth import AuthInfo
from .routes import api_routes
from os.path import dirname
from flask import current_app, session, g
from .utils import es_client
from textwrap import dedent
from .auth import init_auths
from pathlib import Path
from dotenv import load_dotenv
import logging
import yaml
import json
import re

from .models import queries, interests, docs

from .engines.confluence import ConfluenceTitleSearch, ConfluenceMainSpaceSearch
from . import engines

def request_settings():
    g.per_page = current_app.config.get('ENGINE_RESULTS_PER_PAGE', 10)
    g.es = es_client(current_app)

    current_app.logger.info("test")

    confluence_access_token = session.get('confluence_access_token',
        current_app.config.get('CONFLUENCE_ACCESS_TOKEN')
    )

    # create engines dictionary
    g.engines = current_app.config['engines']

    jira_access_token = session.get('jira_access_token',
        current_app.config.get('JIRA_ACCESS_TOKEN')
    )


def create_app(config=None):
    # create app
    app = Flask(__name__, static_url_path="",
        static_folder=dirname(__file__)+"/../frontend/build",
    )
    app.config.from_object(Config)
    app.register_blueprint(api_routes)
    app.before_request(request_settings)

    # update config
    if config is not None:
        app.config.update(config)

    # read config file if present
    if app.config.get('CONFIG_FILE'):
        app.config['FAHNDER'] = yaml.safe_load(Path(app.config.get('CONFIG_FILE')).read_text())

    # update config from config section of fahnder config
    app.config.update(app.config.get('FAHNDER', {}).get('config', {}))

    if is_true(app.config.get('DEBUG', "")):
        logging.getLogger().setLevel(logging.DEBUG)

    logger = logging.getLogger('create_app')

    if app.config.get('ES_DISABLED') is not True:
        # initialize models
        queries.init(app)
        interests.init(app)
        docs.init(app)

        if is_true(app.config.get('TESTING')):
            es = es_client(app)
            es.cluster.put_settings({
                "transient": {
                    "cluster.routing.allocation.disk.watermark.low": "99%",
                    "cluster.routing.allocation.disk.watermark.high": "100%",
                    "cluster.routing.allocation.disk.watermark.flood_stage": "100%",
                    "cluster.info.update.interval": "1m"
                }
            })

    if is_true(app.config.get('TESTING')):
        logger.info("Allow Cross Origin requests")
        # @app.after_request
        # def add_cors_header(response):
        #     header = response.headers
        #     header['Access-Control-Allow-Origin'] = '*'
        #     return response
        # 'true' in CORS-Kopfzeile 'Access-Control-Allow-Credentials' 
        CORS(app, origins = 'http://localhost:3000', resources = '/*', supports_credentials=True)


    # initialize authorization backends
    init_auths(app, app.config['FAHNDER'].get('auths'))

    # initialize engines
    engines.init(app)

    # JSON error handler
    @app.errorhandler(HTTPException)
    def allerrorhandler(e):
        response = e.get_response()
        response.data = json.dumps({
            'code': e.code,
            'name': e.name,
            'error': e.description
        })
        response.content_type = 'application/json'

        return response

    return app

