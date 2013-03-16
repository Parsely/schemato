from distillers import Distill, Distiller

class NewsDistiller(Distiller):
    site = Distill("og:site_name")
    title = Distill("s:headline", "og:title")
    image_url = Distill("s:associatedMedia.ImageObject/url", "og:image")
    pub_date = Distill("s:datePublished")
    author = Distill("s:creator.Person/name", "s:author")
    section = Distill("s:articleSection")
    description = Distill("s:description", "og:description")
    link = Distill("s:url", "og:url")
    id = Distill("s:identifier")

class ParselyDistiller(Distiller):
    site = Distill("og:site_name")
    title = Distill("pp:title", "s:headline", "og:title")
    image_url = Distill("pp:image_url", "s:associatedMedia.ImageObject/url", "og:image")
    pub_date = Distill("pp:pub_date", "s:datePublished")
    author = Distill("pp:author", "s:creator.Person/name")
    section = Distill("pp:section", "s:articleSection")
    link = Distill("pp:link", "og:url")
    post_id = Distill("pp:post_id", "s:identifier")
    page_type = Distill("pp:type")

