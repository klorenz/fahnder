from typing import Union, Any
from datetime import datetime

class Document(dict):

    def __init__(self, 
        type: str,
        url: str,
        title: str = None,
        excerpt: str = None,
        published_at: Union[datetime, str] = None,
        thumbnail_url: str = None,
        mimetype: str = None,
        content: str = None,
        weight: float = 1.0,
        fields: dict = None,
    ):
        """A Search result representation

        Args:
            type (str): Type of the document.
                Can be one of 'page', 'news', 'video', 'image', 'audio'
            url (str):
                Url of the Document
            title (str, optional):
                Title of the document. Defaults to None.
            excerpt (str, optional):
                Excerpt to be displayed. Defaults to None.
            published_at (Union, optional):
                Date of last modification/publishing. Defaults to None.
            thumbnail_url (str, optional):
                Url to a thumbnail. Defaults to None.
            mimetype (str, optional):
                Mimetype. Defaults to None.
            weight (float, optional):
                Weight of this document in search results. Defaults to 1.
            content (str, optional): Content of the document. Defaults to None.
                This is usually not used in a search result, but if you return
                this document as an answer, this is expected.
            fields (dict, optional): extra fields

        """
        assert type in ('page', 'image', 'video', 'news', 'audio', 'issue')

        self['type'] = type
        self['url'] = url
        self['title'] = title
        self['excerpt'] = excerpt
        self['fields'] = fields
        self['published_at'] = published_at
        self['thumbnail_url'] = thumbnail_url
        self['mimetype'] = mimetype
        self['content'] = content
        self['weight'] = weight

