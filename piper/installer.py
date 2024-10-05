import sys
import os
import subprocess
import venv
import site
import importlib
import threading
import logging
import pkg_resources

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class IsolatedEnvironment:
    def __init__(self, venv_path, package_name):
        self.venv_path = venv_path
        self.package_name = package_name
        self.original_sys_path = None
        self.original_sys_prefix = None
        self.original_sys_exec_prefix = None
        self.original_environ = None
        self.original_modules = None
        self.lock = threading.Lock()

    def get_package_dependencies(self):
        pip_output = subprocess.check_output([
            os.path.join(self.venv_path, 'bin', 'pip'),
            'show',
            self.package_name
        ]).decode('utf-8')

        dependencies = []
        for line in pip_output.split('\n'):
            if line.startswith('Requires:'):
                dependencies = [dep.strip() for dep in line.split(':')[1].split(',')]
                break
        return [self.package_name] + dependencies

    def activate(self):
        logger.debug(f"Activating environment: {self.venv_path}")
        self.original_sys_path = sys.path.copy()
        self.original_sys_prefix = sys.prefix
        self.original_sys_exec_prefix = sys.exec_prefix
        self.original_environ = os.environ.copy()
        self.original_modules = sys.modules.copy()

        # Remove all existing site-packages from sys.path
        sys.path = [p for p in sys.path if 'site-packages' not in p and 'dist-packages' not in p]

        # Add the virtual environment to sys.path
        venv_site_packages = os.path.join(self.venv_path, 'lib', f'python{sys.version_info.major}.{sys.version_info.minor}', 'site-packages')
        sys.path.insert(0, venv_site_packages)
        sys.path.insert(0, self.venv_path)

        sys.prefix = sys.exec_prefix = self.venv_path

        bin_dir = 'Scripts' if sys.platform == 'win32' else 'bin'
        os.environ['PATH'] = os.pathsep.join([
            os.path.join(self.venv_path, bin_dir),
            os.environ.get('PATH', '')
        ])
        os.environ['VIRTUAL_ENV'] = self.venv_path

        # Clear modules related to the package and its dependencies
        packages_to_clear = self.get_package_dependencies()
        for module_name in list(sys.modules.keys()):
            if any(module_name.startswith(pkg + '.') or module_name == pkg for pkg in packages_to_clear):
                del sys.modules[module_name]

        logger.debug(f"Updated sys.path: {sys.path}")

    def deactivate(self):
        logger.debug("Deactivating environment")
        sys.path = self.original_sys_path
        sys.prefix = self.original_sys_prefix
        sys.exec_prefix = self.original_sys_exec_prefix
        os.environ.clear()
        os.environ.update(self.original_environ)
        sys.modules.clear()
        sys.modules.update(self.original_modules)

    def __enter__(self):
        self.lock.acquire()
        self.activate()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.deactivate()
        self.lock.release()

def create_venv(venv_path):
    logger.info(f"Creating virtual environment at: {venv_path}")
    venv.create(venv_path, with_pip=True)

def install_package(package_spec, venv_path):
    venv_python = get_venv_python(venv_path)
    logger.info(f"Installing setuptools in {venv_path}")
    subprocess.check_call([venv_python, "-m", "pip", "install", "setuptools"])
    logger.info(f"Installing {package_spec} in {venv_path}")
    subprocess.check_call([venv_python, "-m", "pip", "install", package_spec])


def get_venv_python(venv_path):
    if sys.platform == "win32":
        return os.path.join(venv_path, "Scripts", "python.exe")
    return os.path.join(venv_path, "bin", "python")

def piper_install(package_spec, suffix):
    package_name = package_spec.split('==')[0]
    unique_name = f"{package_name}_{suffix}"
    venv_path = os.path.join(os.getcwd(), 'piper_packages', unique_name)

    create_venv(venv_path)
    install_package(package_spec, venv_path)

    # Create a loader script
    loader_path = os.path.join(os.getcwd(), 'piper_packages', f'{unique_name}_loader.py')
    with open(loader_path, 'w') as f:
        f.write(f"""
import os
import sys
import logging
from piper.installer import IsolatedEnvironment

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

venv_path = {repr(venv_path)}
env = IsolatedEnvironment(venv_path, {repr(package_name)})

def load_module():
    with env:
        logger.debug(f"Current sys.path: {{sys.path}}")
        logger.debug(f"Current working directory: {{os.getcwd()}}")
        try:
            import {package_name} as package_module
            logger.debug(f"Successfully imported {package_name}")
            return package_module
        except ImportError as e:
            logger.error(f"Failed to import {package_name}: {{e}}")
            raise

module = load_module()
""")

    logger.info(f"Successfully installed {package_name} as {unique_name}")
    logger.info(f"You can now import the package as: from piper.piper_import import piper_import; {unique_name} = piper_import('{unique_name}')")
    return unique_name

