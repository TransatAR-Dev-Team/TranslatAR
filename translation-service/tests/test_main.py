import pytest

def test_synchronous_pass():
    """
    Verifies that pytest is set up and running correctly.
    """
    assert True

@pytest.mark.asyncio
async def test_asynchronous_pass():
    """
    Verifies that pytest-asyncio is configured correctly.
    """
    assert "test" == "test"
