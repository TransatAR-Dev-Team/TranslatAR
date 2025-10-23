import pytest


def test_synchronous_pass():
    """
    Verifies that pytest is set up and running correctly.
    """
    assert 1 == 1


@pytest.mark.asyncio
async def test_asynchronous_pass():
    """
    Verifies that pytest-asyncio is configured correctly.
    """
    assert "test" != None
