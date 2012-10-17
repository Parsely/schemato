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
    def __init__(self, graph):
        self.graph = graph
        self.distilled = {}
        # self.distill_fields provided by DistillerMeta
    
    def distill(self):
        for field in self.distill_fields:
            self.distilled[field.name] = self.get_field(field)
        return self.distilled

    def get_field(self, field):
        for path in field.precedence:
            value = self.get_value(path)
            if value is not None:
                return value
        return None

    def parse_path(self, path):
        prefix, field = path.split(":")
        segments = field.split(".")
        return prefix, segments

    def get_value(self, path):
        prefix, segments = self.parse_path(path)
        i = 0
        for segment in segments:
            print " " * i, prefix, segment
            i += 1
        # using self.graph and locator, fetch field


class ParselyDistiller(Distiller):
    title = Distill("pp:title", "s:title", "ogp:title")
    image_url = Distill("pp:image_url", "s:associatedMedia.url", "ogp:image")
    pub_date = Distill("pp:title", "s:datePublished")
    author = Distill("pp:author", "s:creator.name")
    section = Distill("pp:section", "s:articleSection")
    link = Distill("pp:link", "ogp:url")
    post_id = Distill("pp:post_id", "s:identifier")
    page_type = Distill("pp:type")

if __name__ == "__main__":
    from pprint import pprint
    p = ParselyDistiller({})
    pprint(p.distill())
