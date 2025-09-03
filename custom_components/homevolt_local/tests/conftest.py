"""Configuration for pytest."""
import asyncio
import pytest


@pytest.fixture(autouse=True)
def enable_event_loop_debug() -> None:
    """Enable event loop debug mode - Python 3.13 compatible version."""
    try:
        # Try to get the running loop first
        loop = asyncio.get_running_loop()
        loop.set_debug(True)
    except RuntimeError:
        # No running loop, try to create one if needed
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.set_debug(True)
        except Exception:
            # If all fails, just pass - pytest-asyncio will handle it
            pass


# Keep the tests simple without requiring Home Assistant fixtures
