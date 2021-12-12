from fahnder.engine import Engine
from flask import Blueprint, jsonify

blueprint = Blueprint("SimpleSample")

@blueprint.route('/api/simple-sample/ping')
def ping():
    return jsonify(result='pong')

def setup(app):
    app.register_blueprint(blueprint)

class SimpleSample(Engine):
    pass
