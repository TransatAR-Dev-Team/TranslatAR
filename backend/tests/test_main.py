import pytest

def test_app_import():
    """
    Tests that the FastAPI app object can be imported from main.py.
    This confirms that all top-level imports within main.py, including the
    config and websocket modules, are resolved correctly.
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
        from config import DATABASE_URL
    except ImportError as e:
        pytest.fail(f"Failed to import 'DATABASE_URL' from config.py. Error: {e}")

    # Assert that the variable was imported and has a default value
    assert DATABASE_URL is not None
    assert "mongodb://" in DATABASE_URL
