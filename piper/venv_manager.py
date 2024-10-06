# File: piper/venv_manager.py

import os
import sys
import site
import subprocess
import logging

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)

class TemporaryVenvActivation:
    def __init__(self, venv_path):
        self.venv_path = os.path.abspath(venv_path)
        self.original_sys_path = None
        self.original_sys_prefix = None
        self.original_sys_exec_prefix = None
        self.original_os_environ = None
        self.original_modules = None
        self.package_name = os.path.basename(venv_path).split('_')[0]  # Assuming venv name format: package_suffix

    def get_package_dependencies(self):
        pip_path = os.path.join(self.venv_path, 'bin', 'pip')
        if sys.platform == "win32":
            pip_path = os.path.join(self.venv_path, 'Scripts', 'pip.exe')

        try:
            pip_output = subprocess.check_output([pip_path, 'show', self.package_name]).decode('utf-8')
        except subprocess.CalledProcessError:
            logger.error(f"Failed to get dependencies for {self.package_name}")
            return [self.package_name]

        dependencies = []
        for line in pip_output.split('\n'):
            if line.startswith('Requires:'):
                dependencies = [dep.strip() for dep in line.split(':')[1].split(',') if dep.strip()]
                break
        return [self.package_name] + dependencies

    def __enter__(self):
        logger.debug(f"Activating venv: {self.venv_path}")

        # Save the current state
        self.original_sys_path = sys.path.copy()
        self.original_sys_prefix = sys.prefix
        self.original_sys_exec_prefix = sys.exec_prefix
        self.original_os_environ = os.environ.copy()
        self.original_modules = sys.modules.copy()

        # Activate the virtual environment
        bin_dir = 'Scripts' if sys.platform == 'win32' else 'bin'
        os.environ['VIRTUAL_ENV'] = self.venv_path
        os.environ['PATH'] = os.pathsep.join([
            os.path.join(self.venv_path, bin_dir),
            os.environ.get('PATH', '')
        ])
        sys.prefix = sys.exec_prefix = self.venv_path

        # Clear modules related to the package and its dependencies
        packages_to_clear = self.get_package_dependencies()
        for module_name in list(sys.modules.keys()):
            if any(module_name.startswith(pkg + '.') or module_name == pkg for pkg in packages_to_clear):
                del sys.modules[module_name]

        # Update sys.path
        sys.path = [p for p in sys.path if 'site-packages' not in p]
        site_packages = os.path.join(
            self.venv_path, 'Lib', 'site-packages'
        ) if sys.platform == 'win32' else os.path.join(
            self.venv_path, 'lib', f'python{sys.version_info.major}.{sys.version_info.minor}', 'site-packages'
        )
        sys.path.insert(0, site_packages)

        # Run site.main() to set up the environment fully
        old_sys_path = sys.path[:]
        site.main()
        sys.path[:0] = old_sys_path

        logger.debug(f"Updated sys.path: {sys.path}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        logger.debug("Deactivating venv")

        # Restore the original state
        sys.path = self.original_sys_path
        sys.prefix = self.original_sys_prefix
        sys.exec_prefix = self.original_sys_exec_prefix
        os.environ.clear()
        os.environ.update(self.original_os_environ)

        # Restore original modules, effectively clearing any newly imported modules
        sys.modules.clear()
        sys.modules.update(self.original_modules)

def with_venv(venv_path):
    return TemporaryVenvActivation(venv_path)

# The rest of the files (installer.py and cli.py) remain the same as in the previous artifact.
