import importlib.util
import sys
import os

def piper_import(package_name):
    piper_packages_dir = os.path.join(os.getcwd(), 'piper_packages')
    loader_path = os.path.join(piper_packages_dir, f'{package_name}_loader.py')

    if not os.path.exists(loader_path):
        raise ImportError(f"Package '{package_name}' not found in Piper installation")

    spec = importlib.util.spec_from_file_location(package_name, loader_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    return module.module
