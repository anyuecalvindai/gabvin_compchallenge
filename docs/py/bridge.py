"""Single entry point the JavaScript layer talks to.

Every call is module.function(*args) -> JSON string, so the JS side never
holds Python objects and the whole interface stays easy to reason about.
"""
import importlib
import json


def call(path, args_json):
    module_name, func_name = path.rsplit('.', 1)
    module = importlib.import_module(module_name)
    result = getattr(module, func_name)(*json.loads(args_json))
    return json.dumps(result)
