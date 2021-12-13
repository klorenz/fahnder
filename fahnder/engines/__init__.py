import re
from textwrap import dedent
from importlib import import_module

def init(app):
    """This function is called from flask app, when this engine is created.

    Args:
        app (Flask): flask application
    """

    # TODO: think of creating a sandbox

    settings = app.config['FAHNDER']

    # for module in settings.get('modules', []):
    #     module_name = module['name']
    #     assert re.search(r'^\w+(\.\w+)*$', module_name), f"module name invalid: {module_name}"

    #     exec(dedent(f'''\
    #         import {module_name}
    #         if hasattr({module_name}, 'setup'):
    #             {module_name}.setup(app, settings)
    #     '''), globals(), {'settings': module.get(settings, None)})

    app.config['engines'] = {}
    for engine_spec in settings.get('engines', []):
        module = import_module(engine_spec['module'])

        if hasattr(module, 'setup'):
            module.setup(app)

        engine_class = getattr(module, engine_spec['class'])
        engine = engine_class()

        for k,v in engine_spec.get('attributes', {}).items():
            setattr(engine, k, v)

        if hasattr(engine, 'setup'):
            engine.setup(app)

        app.config['engines'][engine_spec['name']] = engine
