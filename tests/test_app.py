from unittest.mock import Mock

import pytest
import pytest_asyncio

from textual_pass.app import App


@pytest_asyncio.fixture
async def app():
    obj = App()
    obj._store = Mock()
    obj._passwords = Mock()
    return obj


@pytest.mark.asyncio
async def test_handle_search_on_change(app):
    message = Mock(sender=Mock(value=Mock(return_value="hello")))
    await app.handle_search_on_change(message)
