VALIDATOR_MODULES = [
    "schemas.rnews.RNewsValidator",
    "schemas.opengraph.OpenGraphValidator",
    "schemas.schemaorg.SchemaOrgValidator",
    "schemas.schemaorg_rdf.SchemaOrgRDFaValidator",
    "schemas.parselypage.ParselyPageValidator",
]

# root of schema cache
CACHE_ROOT = "/tmp"
# how many seconds to wait until re-cache
CACHE_EXPIRY = 60 * 60 * 500
