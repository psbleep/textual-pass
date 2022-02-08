from unittest.mock import AsyncMock, Mock

import pytest
import pytest_asyncio
from textual.keys import Keys

from textual_pass.widgets import Passwords, Search


@pytest.fixture
def passwords():
    passwords = Passwords()
    passwords.listing = ["foo", "bar", "hello", "world"]
    return passwords


@pytest_asyncio.fixture
async def search():
    obj = Search(name="search", title="search: ", value="foobar")
    obj.cursor_position = 3
    obj._emit_on_change = AsyncMock()
    return obj


@pytest.mark.asyncio
async def test_search_beginning_of_line_shortcut(search):
    event = Mock(key=Keys.ControlA)
    await search.on_key(event)
    assert search.cursor_position == 0
    search._emit_on_change.assert_called_with(event)


@pytest.mark.asyncio
async def test_search_end_of_line_shortcut(search):
    event = Mock(key=Keys.ControlE)
    await search.on_key(event)
    assert search.cursor_position == 6
    search._emit_on_change.assert_called_with(event)


@pytest.mark.asyncio
async def test_search_clear_after_cursor_shortcut(search):
    event = Mock(key=Keys.ControlK)
    await search.on_key(event)
    assert search.value == "foo"
    search._emit_on_change.assert_called_with(event)


@pytest.mark.asyncio
async def test_search_clear_until_cursor_shortcut(search):
    event = Mock(key=Keys.ControlU)
    await search.on_key(event)
    assert search.value == "bar"
    assert search.cursor_position == 0
    search._emit_on_change.assert_called_with(event)


@pytest.mark.asyncio
async def test_search_unhandled_key(search):
    event = Mock(key=Keys.ControlBackslash)
    await search.on_key(event)
    search._emit_on_change.assert_not_called()


def test_passwords_get_focused_position(passwords):
    assert passwords.focused_position == 0


def test_passwords_set_focused_position(passwords):
    passwords.focused_position = 2
    assert passwords.focused_position == 2


def test_passwords_set_focused_position_too_low(passwords):
    passwords.focused_position = -1
    assert passwords.focused_position == 0


def test_passwords_set_focused_position_too_high(passwords):
    passwords.focused_position = 4
    assert passwords.focused_position == 3


def test_passwords_set_focused_position_with_no_password_listing(passwords):
    passwords.listing = []
    passwords.focused_position = 2
    assert passwords.focused_position == 0


def test_passwords_get_focused_password(passwords):
    passwords.focused_position = 2
    assert passwords.get_focused_password() == "hello"


def test_passwords_set_focused_position_to_password(passwords):
    passwords.set_focused_position_to_password("world")
    assert passwords.focused_position == 3


def test_passwords_set_focused_position_to_password_that_is_not_listed(passwords):
    passwords.set_focused_position_to_password("zoo")
    assert passwords.focused_position == 3


def test_passwords_render_displays_password_listing_and_highlights_focused_password(
    passwords,
):
    passwords.focused_position = 1
    rendered_panel = passwords.render()
    assert rendered_panel.renderable == "foo\n[bold]bar[/bold]\nhello\nworld"
