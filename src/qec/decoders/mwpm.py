"""
PyMatching implementation of the Minimum Weight
Perfect Matching (MWPM) decoder.

This module provides a common decoder interface
used by the Stim backend.

It supports:

- PyMatching decoding of Stim detector error models.
- Delegation to the reference NetworkX decoder
  for legacy simulations.
"""

import pymatching

from qec.decoders.base import Decoder

from .networkx import (
    decode_one_shot,
    decode_spacetime_one_shot,
)


class MWPMDecoder(Decoder):
    """
    Minimum Weight Perfect Matching decoder.

    Provides a common interface to both the reference 
    NetworkX implementation and the PyMatching decoder
    for Stim detector error models.
    """

    def __init__(
        self,
        backend: str = "networkx",
        dem=None,
    ):
        self.backend = backend

        self.matching = None

        if backend == "pymatching":

            if dem is None:
                raise ValueError(
                    "DEM required for "
                    "PyMatching backend."
                )

            self.matching = (
                pymatching.Matching
                .from_detector_error_model(
                    dem
                )
            )

        elif backend != "networkx":
            raise ValueError(
                f"Unknown backend: "
                f"{backend}"
            )


    def decode(
        self,
        bitstr: str,
        distance: int,
        k: int = 1,
    ) -> tuple[int, int]:
        return decode_one_shot(
            bitstr=bitstr,
            distance=distance,
            k=k,
        )

    def decode_spacetime(
        self,
        bitstr: str,
        distance: int,
        k: int,
    ) -> tuple[int, int]:
        return decode_spacetime_one_shot(
            bitstr=bitstr,
            distance=distance,
            k=k,
        )
    
    def decode_detection_events(
        self,
        detection_events,
    ):
        """
        Decode detector events using
        the PyMatching backend.
        """

        if self.backend != "pymatching":
            raise ValueError(
                "PyMatching backend required."
            )

        return self.matching.decode(
            detection_events
        )