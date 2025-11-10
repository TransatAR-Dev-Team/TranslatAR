import pytest


def test_synchronous_pass():
    """
    A basic synchronous test to confirm pytest is working.
    """
    assert 1 + 1 == 2


@pytest.mark.asyncio
async def test_asynchronous_pass():
    """
    A basic asynchronous test to confirm pytest-asyncio is configured correctly.
    """
    assert "a" + "b" == "ab"
