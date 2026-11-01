"""Expected failures. Their messages are shown to the user as-is."""

DRM_MESSAGE = "This book is DRM-protected; lectr only reads DRM-free files."


class LectrError(Exception):
    """A failure the user can act on; the CLI prints the message and exits 1."""


class BookError(LectrError):
    """The input book cannot be read."""


class ConfigError(LectrError):
    """A setting or the config file is invalid."""


class ModelError(LectrError):
    """The TTS model is missing, unverifiable, or misbehaving."""


class AudioError(LectrError):
    """ffmpeg is missing or failed."""
