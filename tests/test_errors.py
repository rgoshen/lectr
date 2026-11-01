import pytest

from lectr.errors import (
    DRM_MESSAGE,
    AudioError,
    BookError,
    ConfigError,
    LectrError,
    ModelError,
)


def test_drm_message_is_verbatim() -> None:
    assert DRM_MESSAGE == "This book is DRM-protected; lectr only reads DRM-free files."


def test_lectr_error_is_an_exception() -> None:
    assert issubclass(LectrError, Exception)


@pytest.mark.parametrize("error_type", [BookError, ConfigError, ModelError, AudioError])
def test_specific_errors_derive_from_lectr_error(error_type: type[LectrError]) -> None:
    assert issubclass(error_type, LectrError)
