import logging

from django.core.management import BaseCommand, CommandError

from channels import DEFAULT_CHANNEL_LAYER
from channels.layers import get_channel_layer
from channels.routing import get_default_application
from channels.worker import Worker

logger = logging.getLogger("django.channels.worker")


class Command(BaseCommand):
    leave_locale_alone = True
    worker_class = Worker

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):
        # Get the backend to use
        pass
