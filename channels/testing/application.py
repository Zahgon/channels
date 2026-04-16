from unittest import mock

from asgiref.testing import ApplicationCommunicator as BaseApplicationCommunicator


def no_op():
    pass


class ApplicationCommunicator(BaseApplicationCommunicator):
    async def send_input(self, message):
        pass

    async def receive_output(self, timeout=1):
        pass
