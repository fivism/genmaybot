from PIL import Image
from urllib.parse import urlparse


def nsfw_line_parser(self, e):
    """ Watch lines for images to detect nsfw images. """
    url = re.search(r"(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>])*\))+(?:\(([^\s()<>])*\)|[^\s`!()\[\]{};:'\".,<>?«»“”‘’]))", e.input)
    if url:
        url = url.group(0)
        url_parts = urlparse(url)
    else:
        return
nsfw_line_parser.lineparser = True
