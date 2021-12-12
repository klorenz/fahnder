from fahnder.app import create_app 
from fahnder.config import is_true
from fahnder.utils import es_client
import os
import logging
logging.basicConfig()

if __name__ == '__main__':
    app = create_app()
    DEBUG = is_true(app.config.get('DEBUG'))
    logging.getLogger().error("DEBUG=%r", DEBUG)
    app.run(debug=is_true(app.config.get('DEBUG')))
