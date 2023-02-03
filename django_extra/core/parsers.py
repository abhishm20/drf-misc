# -*- coding: utf-8 -*-
from rest_framework.parsers import BaseParser


class XMLParser(BaseParser):
    """
    Plain text parser.
    """

    media_type = "application/xml"

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Simply return a string representing the body of the request.
        """
        return stream.read()
