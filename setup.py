from setuptools import setup, find_packages

with open('README.md', 'r') as f:
    long_description = f.read()

reqs = ['rdflib',
        'lepl',
        'html5lib',
        'lxml',
        ]

setup(
    name = "schemato",
    version = "1.0",
    author = 'Emmet Butler',
    author_email = 'emmett@parsely.com',
    packages=find_packages(exclude=['ez_setup']),
    url='https://github.com/Parsely/schemato',
    keywords='solr solrcloud',
    description='python library for interacting with SolrCloud ',
    long_description=long_description,
    include_package_data=True,
    platforms='any',
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        ],

    install_requires = reqs,

        )
