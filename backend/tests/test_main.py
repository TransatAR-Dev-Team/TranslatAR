import pytest

def test_trivial_assertion():
    """
    A basic synchronous test that is guaranteed to pass.
    This verifies that pytest is being discovered and run correctly.
    """
    print("\nRunning synchronous test...")
    assert 1 == 1
    print("Synchronous test passed.")

@pytest.mark.asyncio
async def test_async_trivial_assertion():
    """
    A basic asynchronous test that is guaranteed to pass.
    This verifies that the pytest-asyncio plugin is configured correctly.
    """
    print("\nRunning asynchronous test...")
    assert True
    print("Asynchronous test passed.")


def test_another_trivial_assertion():
    assert False
