"""
Collaboration Suite - A comprehensive real-time collaboration platform
"""

__version__ = '0.1.0'

# Import main components for easy access
from .client import CollaborationClient
from .server import CollaborationServer

__all__ = ['CollaborationClient', 'CollaborationServer']
