# coding=utf-8
import os
import sys
from glob import glob
from distutils.core import setup

name = 'back_blade'

pjoin = os.path.join
here = os.path.abspath(os.path.dirname(__file__))
root = pjoin(here, 'app')

packages = []
for d, _, _ in os.walk(root):
    if os.path.exists(pjoin(d, '__init__.py')):
        packages.append(d[len(here) + 1:].replace(os.path.sep, '.'))

vinfo = {}
with open(pjoin(root, 'version.py')) as f:
    code = compile(f.read(), "version.py", 'exec')
    exec(code, {}, vinfo)

setup_args = dict(
    name=name,
    version=vinfo['__version__'],
    scripts=glob(pjoin('scripts', '*')),
    packages=packages,
    description="IllumiDesk backend API server",
    long_description="A backend API server for IllumiDesk's LMS workspace manager",
    author="IllumiDesk Development Team",
    author_email="contact@illumidesk.com",
    url="https://github.com/IllumiDesk/app-backend",
    license="BSD-3",
    platforms=["Linux", "Mac OS X", "Windows"],
    keywords=['Interactive', 'Data', 'Science', 'Web', 'Cloud', 'Computing', 'Jupyter'],
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
    ],
)

setuptools_args = {}

with open('requirements/install.txt') as f:
    install_requires = setuptools_args['install_requires'] = f.readlines()

with open('requirements/extras.txt') as f:
    extras_require = setuptools_args['extras_require'] = {}
    for l in f.readlines():
        if not l.startswith("#"):
            extras_require.update(eval("{" + l + "}"))

if 'develop' in sys.argv or any(a.startswith('bdist') for a in sys.argv):
    setup_args.update(setuptools_args)

if __name__ == '__main__':
    setup(**setup_args)
