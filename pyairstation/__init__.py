"""
pyairstation - Python library and CLI tool for managing Buffalo AirStation routers.

This package provides a simple interface to inspect and apply network configurations
based on structured host files.
"""

from .hosts import Host, HostConfig
from .agent import Agent

__version__ = "0.0.1"
__all__ = ["Host", "HostConfig", "Agent"]