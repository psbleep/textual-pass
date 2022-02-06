from unittest.mock import AsyncMock, Mock
import pytest
import pytest_asyncio
from textual.keys import Keys

from textual_pass.widgets import Search


@pytest_asyncio.fixture
async def mock_app():
    obj = AsyncMock()
    await obj.handle_key("hello")
    return obj


@pytest_asyncio.fixture
async def search(mock_app):
    obj = Search(app=mock_app, name="search", title="search: ", value="foobar")
    obj.cursor_position = 3
    return obj


@pytest.mark.asyncio
async def test_search_beginning_of_line_shortcut(search):
    event = Mock(key=Keys.ControlA)
    await search.on_key(event)
    assert search.cursor_position == 0


@pytest.mark.asyncio
async def test_search_end_of_line_shortcut(search):
    event = Mock(key=Keys.ControlE)
    await search.on_key(event)
    assert search.cursor_position == 6


@pytest.mark.asyncio
async def test_search_clear_after_cursor_shortcut(search):
    event = Mock(key=Keys.ControlK)
    await search.on_key(event)
    assert search.value == "foo"


@pytest.mark.asyncio
async def test_search_clear_until_cursor_shortcut(search):
    event = Mock(key=Keys.ControlU)
    await search.on_key(event)
    assert search.value == "bar"
    assert search.cursor_position == 0


@pytest.mark.asyncio
async def test_search_unhandled_key(mock_app, search):
    event = Mock(key=Keys.ControlBackslash)
    await search.on_key(event)
    mock_app.handle_key.assert_called_with(Keys.ControlBackslash)
