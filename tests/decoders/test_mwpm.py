import pytest

from qec.decoders import MWPMDecoder
from qec.stim_backend import SurfaceCodeStimBackend


def test_invalid_backend():

    with pytest.raises(ValueError):

        MWPMDecoder(
            backend="bad",
        )


def test_pymatching_requires_dem():

    with pytest.raises(ValueError):

        MWPMDecoder(
            backend="pymatching",
        )


def test_pymatching_decoder_builds():
    backend = SurfaceCodeStimBackend(
        distance=3,
        rounds=5,
        depolarizing_error=0.01,
    )

    decoder = MWPMDecoder(
        backend="pymatching",
        dem=backend.detector_error_model(),
    )

    assert decoder.matching is not None


def test_pymatching_decode_runs():
    backend = SurfaceCodeStimBackend(
        distance=3,
        rounds=5,
        depolarizing_error=0.01,
    )

    decoder = MWPMDecoder(
        backend="pymatching",
        dem=backend.detector_error_model(),
    )

    dets = backend.sample_detectors(
        shots=1
    )

    result = (
        decoder.decode_detection_events(
            dets[0]
        )
    )

    assert len(result) == 1