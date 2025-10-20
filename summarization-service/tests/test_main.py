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
        from config import OLLAMA_URL, MODEL_NAME
    except ImportError as e:
        pytest.fail(f"Failed to import from config.py. Error: {e}")

    # Assert that the variables were imported and have default values
    assert OLLAMA_URL is not None
    assert MODEL_NAME is not None
    assert "http://" in OLLAMA_URL
