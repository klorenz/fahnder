from typing import Sequence
from .document import Document

class Results(dict):

    def __init__(self, total: int, results=Sequence[Document]):
        self['total'] = total
        self['results'] = results
