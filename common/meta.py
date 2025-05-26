class PaginationMetaData():
    page: int
    per_page: int
    max_page: int
    total: int

    def __init__(self, page, per_page, max_page, total):
        self.page = page
        self.per_page = per_page
        self.max_page = max_page
        self.total = total 

    def json(self):
        return {
            'page': self.page,
            'per_page': self.per_page,
            'max_page': self.max_page,
            'total': self.total
        }