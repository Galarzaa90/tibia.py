import os
import re
import sys

from setuptools import find_packages, setup

if sys.version_info < (3, 6):
    sys.exit('Sorry, Python < 3.6 is not supported')


def get_version(package):
    """Return package version as listed in `__version__` in `init.py`."""
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("__version__ = ['\"]([^'\"]+)['\"]", init_py).group(1)


version = get_version("tibiapy")
if version.endswith(('a', 'b', 'rc')):
    # append version identifier based on commit count
    try:
        import subprocess
        p = subprocess.Popen(['git', 'rev-list', '--count', 'HEAD'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out:
            version += out.decode('utf-8').strip()
        p = subprocess.Popen(['git', 'rev-parse', '--short', 'HEAD'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out:
            version += '+g' + out.decode('utf-8').strip()
    except Exception:
        pass

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.md') as f:
    readme = f.read()

extras_require = {
    'cli': [
        'click',
        'requests',
        'colorama'
    ],
    'docs': [
        'sphinx',
    ],
    'test': [
        'asynctest',
        'aioresponses',
        'coverage'
    ]
}

setup(
    name='tibia.py',
    version=version,
    author='Galarzaa90',
    author_email="allan.galarza@gmail.com",
    url='https://github.com/Galarzaa90/tibia.py',
    license='Apache 2.0',
    install_requires=requirements,
    extras_require=extras_require,
    description="API that parses website content into python data.",
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Games/Entertainment :: Role-Playing',
        'Topic :: Internet',
        'Topic :: Software Development',
        'Topic :: Software Development :: Libraries',
        'Topic :: Text Processing :: Markup :: HTML',
        'Topic :: Utilities'
    ]
)
