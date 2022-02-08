from typing import List, Optional

from rich.panel import Panel
from textual.keys import Keys
from textual.events import Event
from textual.reactive import Reactive
from textual.widget import Widget
from textual_inputs import TextInput


class Search(TextInput):
    _KEY_MAP = {
        Keys.ControlA: "_move_cursor_to_beginning_of_line",
        Keys.ControlE: "_move_cursor_to_end_of_line",
        Keys.ControlK: "_clear_text_after_cursor",
        Keys.ControlU: "_clear_text_before_cursor",
    }

    @property
    def cursor_position(self) -> int:
        return self._cursor_position

    @cursor_position.setter
    def cursor_position(self, position: int) -> None:
        self._cursor_position = position

    async def on_key(self, event: Event) -> None:
        was_handled = await self._handle_key(event.key)
        if was_handled:
            await self._emit_on_change(event)

    async def _handle_key(self, key: Keys) -> bool:
        try:
            method_name = self._KEY_MAP[key]
        except KeyError:
            return False

        method = getattr(self, method_name)
        await method()
        return True

    async def _move_cursor_to_beginning_of_line(self):
        self._cursor_position = 0

    async def _move_cursor_to_end_of_line(self):
        self._cursor_position = len(self.value)

    async def _clear_text_after_cursor(self):
        self.value = self.value[: self._cursor_position]

    async def _clear_text_before_cursor(self):
        self.value = self.value[self._cursor_position :]
        self._cursor_position = 0


class Passwords(Widget):
    _focused_position: Reactive[int] = Reactive(0)
    listing: Reactive[List[str]] = Reactive([])

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


class Output(Widget):
    output: Reactive[str] = Reactive("")

    def render(self) -> Panel:
        return Panel(self.output)
