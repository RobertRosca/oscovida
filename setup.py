# -*- coding: utf-8 -*-

# DO NOT EDIT THIS FILE!
# This file has been autogenerated by dephell <3
# https://github.com/dephell/dephell

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


import os.path

readme = ''
here = os.path.abspath(os.path.dirname(__file__))
readme_path = os.path.join(here, 'README.rst')
if os.path.exists(readme_path):
    with open(readme_path, 'rb') as stream:
        readme = stream.read().decode('utf8')


setup(
    long_description=readme,
    name='oscovida',
    version='0.1.2',
    description='Explore COVID19 case numbers and deaths related to Coronavirus outbreak 2019/2020 in Pandas and in Jupyter notebook with MyBinder',
    python_requires='==3.*,>=3.7.0',
    project_urls={"homepage": "https://github.com/oscovida/oscovida"},
    author='Hans Fangohr',
    author_email='da-support@xfel.eu',
    maintainer='Robert Rosca',
    license='BSD-3-Clause',
    classifiers=[
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Information Analysis',
    ],
    packages=['oscovida', 'oscovida.plots'],
    package_dir={"": "src"},
    package_data={},
    install_requires=[
        'appdirs==1.*,>=1.4.4',
        'fastcore==1.*,>=1.3.1',
        'matplotlib<3.3',
        'numpy==1.*,>=1.19.0',
        'pandas==1.*,>=1.1.0',
        'pycountry==20.*,>=20.7.3',
        'requests==2.*,>=2.24.0',
        'scipy==1.*,>=1.5.3',
    ],
    extras_require={
        "dev": [
            "black==19.*,>=19.10.0.b0",
            "coverage==5.*,>=5.2.0",
            "dephell==0.*,>=0.8.3",
            "hypothesis==5.*,>=5.32.0",
            "ipython==7.*,>=7.16.1",
            "isort==5.*,>=5.4.2",
            "jupyterlab==2.*,>=2.2.0",
            "kaleido==0.*,>=0.0.3",
            "mkdocs==1.*,>=1.1.2",
            "mkdocs-material==5.*,>=5.5.12",
            "mkdocstrings==0.*,>=0.13.2",
            "mknotebooks==0.*,>=0.6.2",
            "mutmut==2.*,>=2.1.0",
            "nbval==0.*,>=0.9.5",
            "plotly==4.*,>=4.9.0",
            "pre-commit==2.*,>=2.7.1",
            "psutil==5.*,>=5.7.2",
            "pygments==2.*,>=2.7.2",
            "pymdown-extensions==8.*,>=8.0.1",
            "pytest==5.*,>=5.4.3",
            "pytest-cov==2.*,>=2.10.0",
            "testpath==0.*,>=0.4.4",
        ],
        "docs": [
            "mkdocs==1.*,>=1.1.2",
            "mkdocs-material==5.*,>=5.5.12",
            "mkdocstrings==0.*,>=0.13.2",
            "mknotebooks==0.*,>=0.6.2",
            "pygments==2.*,>=2.7.2",
            "pymdown-extensions==8.*,>=8.0.1",
        ],
        "formatting": [
            "black==19.*,>=19.10.0.b0",
            "dephell==0.*,>=0.8.3",
            "isort==5.*,>=5.4.2",
            "pre-commit==2.*,>=2.7.1",
        ],
        "plotly": [
            "kaleido==0.*,>=0.0.3",
            "plotly==4.*,>=4.9.0",
            "psutil==5.*,>=5.7.2",
        ],
        "test": [
            "coverage==5.*,>=5.2.0",
            "hypothesis==5.*,>=5.32.0",
            "mutmut==2.*,>=2.1.0",
            "nbval==0.*,>=0.9.5",
            "pytest==5.*,>=5.4.3",
            "pytest-cov==2.*,>=2.10.0",
            "testpath==0.*,>=0.4.4",
        ],
    },
)
