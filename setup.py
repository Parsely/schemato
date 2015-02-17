from setuptools import setup


install_requires = [
    'rdflib',
    'lepl',
    'lxml',
    'six',
]
schemato_validators = [
    'rnews=schemato.schemas.rnews:RNewsValidator',
    'opengraph=schemato.schemas.opengraph:OpenGraphValidator',
    'schemaorg=schemato.schemas.schemaorg:SchemaOrgValidator',
    'schemaorg_rdf=schemato.schemas.schemaorg_rdf:SchemaOrgRDFaValidator',
    'parselypage=schemato.schemas.parselypage:ParselyPageValidator',
]

setup(
    name="schemato",
    version="1.2.0",
    author='Emmett Butler',
    author_email='emmett@parsely.com',
    url='https://github.com/Parsely/schemato',
    keywords='microdata rdf metadata',
    packages=['schemato', 'schemato.schemas'],
    description='Unified semantic metadata validator',
    platforms='any',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires=install_requires,
    entry_points={'schemato_validators': schemato_validators}
)
