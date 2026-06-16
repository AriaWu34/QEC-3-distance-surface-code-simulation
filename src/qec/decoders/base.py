"""
Abstract base class for decoder implementations.
"""

from abc import ABC, abstractmethod


class Decoder(ABC):
    """
    Interface for syndrome decoders.
    """

    @abstractmethod
    def decode(self, *args, **kwargs):
        """
        Decode syndrome information and return logical outcomes.
        """
        pass