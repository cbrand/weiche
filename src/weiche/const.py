try:
    from weiche.version import __version__
except ImportError:  # pragma: no cover
    __version__ = "0.0.0"

DEFAULT_BASE_URL = "https://int.bahn.de/web/api/"
USER_AGENT = f"weiche/{__version__}"
TLS_ECDH_CURVE = "X25519"
