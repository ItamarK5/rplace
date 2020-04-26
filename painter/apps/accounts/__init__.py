from __future__ import absolute_import
"""
name: accounts
used to handle staff related to login, register, change password and exc..
"""

from .router import accounts_router
from . import urls


__all__ = ['accounts_router']
