import pytest

def test_trivial_assertion():
    assert 1 == 1

@pytest.mark.asyncio
async def test_async_trivial_assertion():
    assert True
