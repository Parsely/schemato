RNEWS_ROOT = "http://iptc.org/std/rNews/2011-10-07#"
SCHEMA_ROOT = "http://schema.org/"
OG_ROOT = "http://ogp.me/ns#"
OG_ALT_ROOT = "http://opengraphprotocol.org/schema/"
RDFA_NAMESPACES = [RNEWS_ROOT, OG_ROOT, OG_ALT_ROOT]
MICRODATA_NAMESPACES = [SCHEMA_ROOT]

COMMON_PREFIXES = ['og:', 'rnews:']

ns2ont = {RNEWS_ROOT: "http://dev.iptc.org/files/rNews/rnews_1.0_draft3_rdfxml.owl",
        SCHEMA_ROOT: "http://schema.org/docs/schema_org_rdfa.html",
        OG_ROOT: "http://ogp.me/ns/ogp.me.ttl",
        OG_ALT_ROOT: "http://ogp.me/ns/ogp.me.ttl"}
