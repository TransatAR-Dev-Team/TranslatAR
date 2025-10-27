import pytest


def test_synchronous_pass():
    """
    Verifies that pytest is set up and running correctly.
    """
    assert "hello" != "world"


@pytest.mark.asyncio
async def test_asynchronous_pass():
    """
    Verifies that pytest-asyncio is configured correctly.
    """
    assert 1 == 1
