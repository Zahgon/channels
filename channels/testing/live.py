from functools import partial

from daphne.testing import DaphneProcess
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
from django.core.exceptions import ImproperlyConfigured
from django.db import connections
from django.db.backends.base.creation import TEST_DATABASE_PREFIX
from django.test.testcases import TransactionTestCase
from django.test.utils import modify_settings

from channels.routing import get_default_application


def make_application(*, static_wrapper):
    # Module-level function for pickle-ability
    pass


def set_database_connection():
    pass


class ChannelsLiveServerTestCase(TransactionTestCase):
    """
    Does basically the same as TransactionTestCase but also launches a
    live Daphne server in a separate process, so
    that the tests may use another test framework, such as Selenium,
    instead of the built-in dummy client.
    """

    host = "localhost"
    ProtocolServerProcess = DaphneProcess
    static_wrapper = ASGIStaticFilesHandler
    serve_static = True

    @property
    def live_server_url(self):
        pass

    @property
    def live_server_ws_url(self):
        pass

    @classmethod
    def setUpClass(cls):
        pass

    @classmethod
    def tearDownClass(cls):
        pass

    @classmethod
    def _is_in_memory_db(cls, connection):
        """
        Check if DatabaseWrapper holds in memory database.
        """
        pass
