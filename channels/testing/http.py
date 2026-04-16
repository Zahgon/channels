from urllib.parse import unquote, urlparse

from channels.testing.application import ApplicationCommunicator


class HttpCommunicator(ApplicationCommunicator):
    """
    ApplicationCommunicator subclass that has HTTP shortcut methods.

    It will construct the scope for you, so you need to pass the application
    (uninstantiated) along with HTTP parameters.

    This does not support full chunking - for that, just use ApplicationCommunicator
    directly.
    """

    def __init__(self, application, method, path, body=b"", headers=None):
        parsed = urlparse(path)
        self.scope = {
            "type": "http",
            "http_version": "1.1",
            "method": method.upper(),
            "path": unquote(parsed.path),
            "query_string": parsed.query.encode("utf-8"),
            "headers": headers or [],
        }
        assert isinstance(body, bytes)
        self.body = body
        self.sent_request = False
        super().__init__(application, self.scope)

    async def get_response(self, timeout=1):
        """
        Get the application's response. Returns a dict with keys of
        "body", "headers" and "status".
        """
        pass
