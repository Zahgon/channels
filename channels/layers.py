import asyncio
import fnmatch
import random
import re
import string
import time
import warnings
from copy import deepcopy

from django.conf import settings
from django.core.signals import setting_changed
from django.utils.module_loading import import_string

from channels import DEFAULT_CHANNEL_LAYER

from .exceptions import ChannelFull, InvalidChannelLayerError


class ChannelLayerManager:
    """
    Takes a settings dictionary of backends and initialises them on request.
    """

    def __init__(self):
        self.backends = {}
        setting_changed.connect(self._reset_backends)

    def _reset_backends(self, setting, **kwargs):
        """
        Removes cached channel layers when the CHANNEL_LAYERS setting changes.
        """
        pass

    @property
    def configs(self):
        # Lazy load settings so we can be imported
        pass

    def make_backend(self, name):
        """
        Instantiate channel layer.
        """
        pass

    def make_test_backend(self, name):
        """
        Instantiate channel layer using its test config.
        """
        pass

    def _make_backend(self, name, config):
        # Check for old format config
        pass

    def __getitem__(self, key):
        if key not in self.backends:
            self.backends[key] = self.make_backend(key)
        return self.backends[key]

    def __contains__(self, key):
        return key in self.configs

    def set(self, key, layer):
        """
        Sets an alias to point to a new ChannelLayerWrapper instance, and
        returns the old one that it replaced. Useful for swapping out the
        backend during tests.
        """
        pass


class BaseChannelLayer:
    """
    Base channel layer class that others can inherit from, with useful
    common functionality.
    """

    MAX_NAME_LENGTH = 100

    def __init__(self, expiry=60, capacity=100, channel_capacity=None):
        self.expiry = expiry
        self.capacity = capacity
        self.channel_capacity = channel_capacity or {}

    def compile_capacities(self, channel_capacity):
        """
        Takes an input channel_capacity dict and returns the compiled list
        of regexes that get_capacity will look for as self.channel_capacity
        """
        pass

    def get_capacity(self, channel):
        """
        Gets the correct capacity for the given channel; either the default,
        or a matching result from channel_capacity. Returns the first matching
        result; if you want to control the order of matches, use an ordered dict
        as input.
        """
        for pattern, capacity in self.channel_capacity:
            if pattern.match(channel):
                return capacity
        return self.capacity

    def match_type_and_length(self, name):
        if isinstance(name, str) and (len(name) < self.MAX_NAME_LENGTH):
            return True
        return False

    # Name validation functions

    channel_name_regex = re.compile(r"^[a-zA-Z\d\-_.]+(\![\d\w\-_.]*)?$")
    group_name_regex = re.compile(r"^[a-zA-Z\d\-_.]+$")
    invalid_name_error = (
        "{} name must be a valid unicode string "
        + "with length < {} ".format(MAX_NAME_LENGTH)
        + "containing only ASCII alphanumerics, hyphens, underscores, or periods."
    )

    def require_valid_channel_name(self, name, receive=False):
        if not self.match_type_and_length(name):
            raise TypeError(self.invalid_name_error.format("Channel"))
        if not bool(self.channel_name_regex.match(name)):
            raise TypeError(self.invalid_name_error.format("Channel"))
        if "!" in name and not name.endswith("!") and receive:
            raise TypeError("Specific channel names in receive() must end at the !")
        return True

    def require_valid_group_name(self, name):
        pass

    def valid_channel_names(self, names, receive=False):
        pass

    def non_local_name(self, name):
        """
        Given a channel name, returns the "non-local" part. If the channel name
        is a process-specific channel (contains !) this means the part up to
        and including the !; if it is anything else, this means the full name.
        """
        pass

    async def send(self, channel, message):
        raise NotImplementedError("send() should be implemented in a channel layer")

    async def receive(self, channel):
        raise NotImplementedError("receive() should be implemented in a channel layer")

    async def new_channel(self):
        raise NotImplementedError(
            "new_channel() should be implemented in a channel layer"
        )

    async def flush(self):
        raise NotImplementedError("flush() not implemented (flush extension)")

    async def group_add(self, group, channel):
        raise NotImplementedError("group_add() not implemented (groups extension)")

    async def group_discard(self, group, channel):
        raise NotImplementedError("group_discard() not implemented (groups extension)")

    async def group_send(self, group, message):
        raise NotImplementedError("group_send() not implemented (groups extension)")

    # Deprecated methods.
    def valid_channel_name(self, channel_name, receive=False):
        """
        Deprecated: Use require_valid_channel_name instead.
        """
        pass

    def valid_group_name(self, group_name):
        """
        Deprecated: Use require_valid_group_name instead..
        """
        pass


class InMemoryChannelLayer(BaseChannelLayer):
    """
    In-memory channel layer implementation
    """

    def __init__(
        self,
        expiry=60,
        group_expiry=86400,
        capacity=100,
        channel_capacity=None,
        **kwargs,
    ):
        super().__init__(
            expiry=expiry,
            capacity=capacity,
            channel_capacity=channel_capacity,
            **kwargs,
        )
        self.channels = {}
        self.groups = {}
        self.group_expiry = group_expiry

    # Channel layer API

    extensions = ["groups", "flush"]

    async def send(self, channel, message):
        """
        Send a message onto a (general or specific) channel.
        """
        # Typecheck
        assert isinstance(message, dict), "message is not a dict"
        self.require_valid_channel_name(channel)
        # If it's a process-local channel, strip off local part and stick full
        # name in message
        assert "__asgi_channel__" not in message

        queue = self.channels.setdefault(
            channel, asyncio.Queue(maxsize=self.get_capacity(channel))
        )
        # Add message
        try:
            queue.put_nowait((time.time() + self.expiry, deepcopy(message)))
        except asyncio.queues.QueueFull:
            raise ChannelFull(channel)

    async def receive(self, channel):
        """
        Receive the first message that arrives on the channel.
        If more than one coroutine waits on the same channel, a random one
        of the waiting coroutines will get the result.
        """
        pass

    async def new_channel(self, prefix="specific."):
        """
        Returns a new channel name that can be used by something in our
        process as a specific channel.
        """
        pass

    # Expire cleanup

    def _clean_expired(self):
        """
        Goes through all messages and groups and removes those that are expired.
        Any channel with an expired message is removed from all groups.
        """
        pass

    # Flush extension

    async def flush(self):
        self.channels = {}
        self.groups = {}

    async def close(self):
        # Nothing to go
        pass

    def _remove_from_groups(self, channel):
        """
        Removes a channel from all groups. Used when a message on it expires.
        """
        pass

    # Groups extension

    async def group_add(self, group, channel):
        """
        Adds the channel name to a group.
        """
        pass

    async def group_discard(self, group, channel):
        # Both should be text and valid
        pass

    async def group_send(self, group, message):
        # Check types
        pass


def get_channel_layer(alias=DEFAULT_CHANNEL_LAYER):
    """
    Returns a channel layer by alias, or None if it is not configured.
    """
    try:
        return channel_layers[alias]
    except KeyError:
        return None


# Default global instance of the channel layer manager
channel_layers = ChannelLayerManager()
