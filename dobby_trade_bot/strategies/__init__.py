import importlib
import os


def get_strategy(name):
    for dirpath, _, filenames in os.walk(os.path.dirname(__file__)):
        filename: str
        for filename in filenames:
            if filename.endswith("_strategy.py"):
                if filename.replace("_strategy.py", "") == name:
                    spec = importlib.util.spec_from_file_location(name, os.path.join(dirpath, filename))
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    return module.Strategy
    return None
