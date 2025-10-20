import pytest

def test_app_import():
    """
    Tests that the FastAPI app object can be imported from main.py.
    This confirms that all top-level imports within main.py, including the
    config module, are resolved correctly.
    """
    try:
        from main import app
    except ImportError as e:
        pytest.fail(f"Failed to import 'app' from main.py. Error: {e}")
    
    assert app is not None

def test_config_import():
    """
    Tests that configuration variables can be imported directly from the config module.
    This confirms that the config.py file is accessible.
    """
    try:
        from config import LIBRETRANSLATE_URL
    except ImportError as e:
        pytest.fail(f"Failed to import 'LIBRETRANSLATE_URL' from config.py. Error: {e}")

    # Assert that the variable was imported and has a default value
    assert LIBRETRANSLATE_URL is not None
    assert "http://" in LIBRETRANSLATE_URL
