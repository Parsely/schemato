from rdflib.term import URIRef
from six import with_metaclass, iteritems


class Distill(object):
    def __init__(self, *precedence, **kwargs):
        self.precedence = precedence

    def __repr__(self):
        return "Distill(name={0}, precedence={1})".format(
            self.name, self.precedence)


class DistillerMeta(type):
    def __new__(meta, classname, bases, class_dict):
        distill_fields = []
        for name, value in iteritems(class_dict):
            if isinstance(value, Distill):
                if getattr(value, "name", None) is None:
                    value.name = name
                distill_fields.append(value)
        class_dict["distill_fields"] = distill_fields
        return type.__new__(meta, classname, bases, class_dict)


class Distiller(with_metaclass(DistillerMeta, object)):

    def __init__(self, schemato):
        self.schemato = schemato
        self.distilled = {}
        self.sources = {}
        # self.distill_fields provided by DistillerMeta

    def distill(self):
        for field in self.distill_fields:
            value, path = self.get_field(field)
            self.distilled[field.name] = value
            self.sources[field.name] = path
        return self.distilled

    def get_field(self, field):
        for path in field.precedence:
            value = self.get_value(path)
            if value is not None:
                return value, path
        return (None, None)

    PATH_PREFIX = {
        "pp": "get_parsely_page",
        "s": "get_schema_org",
        "og": "get_open_graph"
    }

    def parse_path(self, path):
        prefix, field = path.split(":")
        segments = field.split(".")
        return prefix, segments

    def get_parsely_page(self, segments):
        # for pp, we don't support nesting, so there will always
        # be a single segment
        assert len(segments) == 1
        key = segments[0]
        pp = self.schemato.parsely_page
        if pp is not None and key in pp:
            return pp[key]

    def get_open_graph(self, segments):
        # for opengraph, no nesting
        assert len(segments) == 1
        key = segments[0]
        graph = self.schemato.graph.rdfa_graph
        matches = graph.triples(
            (None, URIRef("http://ogp.me/ns#{key}".format(key=key)), None)
        )
        for match in matches:
            subj, pred, obj = match
            return ''.join((obj,)).encode('utf-8')

    def get_schema_org(self, segments):
        graph = self.schemato.graph.microdata_graph
        if len(segments) == 1:
            segment = segments[0]
            matches = graph.triples(
                (None,
                 URIRef("http://schema.org/{key}".format(key=segment)),
                 None)
            )
            match = next(matches, None)
            if match is None:
                return
            subj, pred, obj = match
            return ''.join((obj,)).encode('utf-8')
        elif len(segments) == 2:
            root, nested = segments
            discriminator, field = nested.split("/")
            typematches = graph.triples(
                (None,
                 URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"),
                 URIRef("http://schema.org/{key}".format(key=discriminator)))
            )
            if field == "url":
                for match in typematches:
                    subj, pred, obj = match
                    if isinstance(subj, URIRef):
                        return ''.join((subj,)).encode('utf-8')
                return
            else:
                typematch = next(typematches, (None, None, None))
                subj, pred, obj = typematch
                if subj is None:
                    return
                valmatches = graph.triples(
                    (subj,
                     URIRef("http://schema.org/{key}".format(key=field)),
                     None)
                )
                valmatch = next(valmatches, (None, None, None))
                subj, pred, obj = valmatch
                if obj is None:
                    return
                return ''.join((obj,)).encode('utf-8')
        else:
            raise NotImplementedError(
                "Only 1 or 2 path segments currently supported")

    def get_value(self, path):
        prefix, segments = self.parse_path(path)
        method_name = self.PATH_PREFIX[prefix]
        method = getattr(self, method_name)
        ret = method(segments)
        return ret
