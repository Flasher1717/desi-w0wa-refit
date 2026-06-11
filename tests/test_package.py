"""Bootstrap sanity test: the package imports and exposes a version."""

import desi_w0wa_refit


def test_package_has_version() -> None:
    assert desi_w0wa_refit.__version__ == "0.1.0"
