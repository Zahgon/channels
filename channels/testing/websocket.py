import json
from urllib.parse import unquote, urlparse

from channels.testing.application import ApplicationCommunicator


class WebsocketCommunicator(ApplicationCommunicator):
    """
    ApplicationCommunicator subclass that has WebSocket shortcut methods.

    It will construct the scope for you, so you need to pass the application
    (uninstantiated) along with the initial connection parameters.
    """

    def __init__(
        self, application, path, headers=None, subprotocols=None, spec_version=None
    ):
        if not isinstance(path, str):
            raise TypeError("Expected str, got {}".format(type(path)))
        parsed = urlparse(path)
        self.scope = {
            "type": "websocket",
            "path": unquote(parsed.path),
            "query_string": parsed.query.encode("utf-8"),
            "headers": headers or [],
            "subprotocols": subprotocols or [],
        }
        if spec_version:
            self.scope["spec_version"] = spec_version
        super().__init__(application, self.scope)
        self.response_headers = None

    async def connect(self, timeout=1):
        """
        Trigger the connection code.

        On an accepted connection, returns (True, <chosen-subprotocol>)
        On a rejected connection, returns (False, <close-code>)
        """
        pass

    async def send_to(self, text_data=None, bytes_data=None):
        """
        Sends a WebSocket frame to the application.
        """
        pass

    async def send_json_to(self, data):
        """
        Sends JSON data as a text frame
        """
        pass

    async def receive_from(self, timeout=1):
        """
        Receives a data frame from the view. Will fail if the connection
        closes instead. Returns either a bytestring or a unicode string
        depending on what sort of frame you got.
        """
        pass

    async def receive_json_from(self, timeout=1):
        """
        Receives a JSON text frame payload and decodes it
        """
        pass

    async def disconnect(self, code=1000, timeout=1):
        """
        Closes the socket
        """
        pass
