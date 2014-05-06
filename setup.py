from distutils.core import setup

with open('README.md', 'r') as f:
    long_description = f.read()

reqs = ['rdflib',
        'lepl',
        'html5lib',
        'lxml',
        ]

setup(
    name="schemato",
    version="1.1",
    author='Emmett Butler',
    author_email='emmett@parsely.com',
    url='https://github.com/Parsely/schemato',
    keywords='microdata rdf metadata',
    packages=['schemato'],
    description='Unified semantic metadata validator',
    long_description=long_description,
    platforms='any',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    requires=reqs
)
