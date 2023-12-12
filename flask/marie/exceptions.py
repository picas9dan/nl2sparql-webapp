class BaseError(Exception):
    def __init__(self, message: str, code: int, detail: str = ""):
        super().__init__(message)
        self.message = message
        self.code = code
        self.detail = detail

    def to_dict(self):
        return dict(
            error=dict(code=self.code, type=type(self).__name__, message=self.message, detail=self.detail)
        )


class KgConnectionError(BaseError):
    def __init__(self):
        super().__init__("Unable to connect to knowledge base.", 500)


class QueryBadFormedError(BaseError):
    def __init__(self, detail):
        super().__init__("Query is badly formed.", 400, detail=detail)
