from typing import List, Optional

from rich.panel import Panel
from textual.events import Event
from textual.keys import Keys
from textual.reactive import Reactive
from textual.widget import Widget
from textual_inputs import TextInput


class Search(TextInput):
    def __init__(self, app, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._app = app

    @property
    def cursor_position(self) -> int:
        return self._cursor_position

    @cursor_position.setter
    def cursor_position(self, position: int) -> None:
        self._cursor_position = position

    async def on_key(self, event: Event) -> None:
        handled = await self._handle_on_key(event)
        if handled:
            await self._emit_on_change(event)
        else:
            await self._app.handle_key(event.key)

    async def _handle_on_key(self, event: Event) -> bool:
        if event.key == Keys.ControlA:
            self._cursor_position = 0
        elif event.key == Keys.ControlE:
            self._cursor_position = len(self.value)
        elif event.key == Keys.ControlK:
            self.value = self.value[: self._cursor_position]
        elif event.key == Keys.ControlU:
            self.value = self.value[self._cursor_position :]
            self._cursor_position = 0
        else:
            return False

        return True

    async def clear_search_term(self, event: Event) -> None:
        self._cursor_position = 0
        self.value = ""
        await self._emit_on_change(event)


class Passwords(Widget):
    _focused_position: Reactive[int] = Reactive(0)
    listing: Reactive[List[str]] = Reactive([])

    def __init__(self, app, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._app = app

    @property
    def focused_position(self) -> int:
        return self._focused_position

    @focused_position.setter
    def focused_position(self, value: int) -> None:
        if value < 0:
            self._focused_position = 0
            return

        self._focused_position = min([self._max_focused_position, value])

    @property
    def _max_focused_position(self) -> int:
        return max(0, len(self.listing) - 1)

    def get_focused_password(self) -> Optional[str]:
        return self.listing[self.focused_position]

    def set_focused_position_to_password(self, password: str) -> None:
        try:
            self.focused_position = self.listing.index(password)
        except ValueError:
            self.focused_position = self._max_focused_position

    def render(self) -> Panel:
        output_lines = self._get_output_lines()
        return Panel("\n".join(output_lines))

    def _get_output_lines(self) -> List[str]:
        output_lines = []
        for idx, line in enumerate(self.listing):
            if idx == self.focused_position:
                line = f"[bold]{line}[/bold]"
            output_lines.append(line)
        return output_lines

    async def on_key(self, event: Event) -> None:
        await self._app.handle_key(event.key)


class Output(Widget):
    output: Reactive[str] = Reactive("")

    def render(self) -> Panel:
        return Panel(self.output)
