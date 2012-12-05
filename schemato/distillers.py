from rdflib.term import URIRef, BNode

class Distill(object):
    def __init__(self, *precedence, **kwargs):
        self.precedence = precedence
        if "name" in kwargs:
            self.name = name
        # otherwise, self.name provided by DistillerMeta

    def __repr__(self):
        return "Distill(name={0}, precedence={1})".format(self.name, self.precedence)

class DistillerMeta(type):
    def __new__(meta, classname, bases, class_dict):
        distill_fields = []
        for name, value in class_dict.iteritems():
            if isinstance(value, Distill):
                if getattr(value, "name", None) is None:
                    value.name = name
                distill_fields.append(value)
        class_dict["distill_fields"] = distill_fields
        return type.__new__(meta, classname, bases, class_dict)

class Distiller(object):
    __metaclass__ = DistillerMeta

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
            return str(obj)
        return None

    def get_schema_org(self, segments):
        graph = self.schemato.graph.microdata_graph
        if len(segments) == 1:
            segment = segments[0]
            matches = graph.triples(
                (None, URIRef("http://schema.org/{key}".format(key=segment)), None)
            )
            match = None
            try:
                match = matches.next()
            except StopIteration:
                pass
            if match is None:
                return None
            subj, pred, obj = match
            return str(obj)
        elif len(segments) == 2:
            root, nested = segments
            discriminator, field = nested.split("/")
            typematches = graph.triples(
                (None,  URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"), URIRef("http://schema.org/{key}".format(key=discriminator)))
            )
            if field == "url":
                for match in typematches:
                    subj, pred, obj = match
                    if isinstance(subj, URIRef):
                        return str(subj)
                return None
            else:
                typematch = None
                try:
                    typematch = typematches.next()
                except StopIteration:
                    typematch = (None, None, None)
                subj, pred, obj = typematch
                if subj is None:
                    return None
                valmatches = graph.triples(
                    (subj, URIRef("http://schema.org/{key}".format(key=field)), None)
                )
                valmatch = None
                try:
                    valmatch = valmatches.next()
                except StopIteration:
                    valmatch = (None, None, None)
                subj, pred, obj = valmatch
                if obj is None:
                    return None
                return str(obj)
        else:
            raise NotImplemented("Only 1 or 2 path segments currently supported")

    def get_value(self, path):
        prefix, segments = self.parse_path(path)
        i = 0
        method_name = self.PATH_PREFIX[prefix]
        method = getattr(self, method_name)
        for segment in segments:
            print " " * i, prefix, segment
            i += 1
        ret = method(segments)
        if ret is not None:
            print " " * i + " -> " + ret
        return ret

