from typing import Union
from dateutil.parser import parse as dt_parse
from datetime import datetime

class SearchRequest:

    def __init__(self, 
        category: str = None, 
        query: str = None, 
        q: str = None,
        page: Union[int, str] = None, 
        before: Union[datetime, str] = None, 
        after: Union[datetime, str] = None, 
        per_page: Union[int, str] = 5,
        ):

        self.query = None
        if q is not None:
            self.query = q
        if query is not None:
            self.query = query

        self.category = category
        self.page = int(page)

        if after is not None and not isinstance(after, datetime):
            after = dt_parse(after)

        self.after = after
        if before is not None and not isinstance(after, datetime):
            self.before = dt_parse(before)

        self.per_page = int(per_page)

    def __repr__(self):
        return (
            f"query={self.query}, category={self.category}, "
            f"after={self.after}, before={self.before}, "
            f"page={self.page}, per_page={self.per_page}"
        )
