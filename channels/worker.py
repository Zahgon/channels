import asyncio

from asgiref.server import StatelessServer


class Worker(StatelessServer):
    """
    ASGI protocol server that surfaces events sent to specific channels
    on the channel layer into a single application instance.
    """

    def __init__(self, application, channels, channel_layer, max_applications=1000):
        super().__init__(application, max_applications)
        self.channels = channels
        self.channel_layer = channel_layer
        if self.channel_layer is None:
            raise ValueError("Channel layer is not valid")

    async def handle(self):
        """
        Listens on all the provided channels and handles the messages.
        """
        pass

    async def listener(self, channel):
        """
        Single-channel listener
        """
        pass
