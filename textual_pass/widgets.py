from typing import Callable, List, Optional, Tuple

from rich.panel import Panel
from textual.events import Event
from textual.keys import Keys
from textual.reactive import Reactive
from textual.widget import Widget
from textual_inputs import TextInput


class PromptShortcutsMixin:
    _SHORTCUTS_MAP = {
        Keys.ControlA: "_move_cursor_to_beginning_of_line",
        Keys.ControlE: "_move_cursor_to_end_of_line",
        Keys.ControlK: "_clear_text_after_cursor",
        Keys.ControlU: "_clear_text_before_cursor",
    }

    async def on_key(self, event: Event) -> None:
        was_handled = await self._handle_key(event.key)
        if was_handled:
            await self._emit_on_change(event)

    async def _handle_key(self, key: Keys) -> bool:
        try:
            method_name = self._SHORTCUTS_MAP[key]
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


class Search(PromptShortcutsMixin, TextInput):
    @property
    def cursor_position(self) -> int:
        return self._cursor_position

    @cursor_position.setter
    def cursor_position(self, position: int) -> None:
        self._cursor_position = position


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


class _ConsolePrompt:
    def __init__(
        self,
        prompt: str,
        response: str = "",
        parse: Optional[Callable] = None,
        validate: Optional[Callable] = None,
    ) -> None:
        self.prompt = prompt
        self.response = response
        self.parse = parse
        self.validate = validate

    def __call__(self, key: Keys) -> None:
        self.response += key
        return True

    def __str__(self) -> str:
        return f"{self.prompt}: {self.response}"

    def save(self) -> Tuple[bool, Optional[str]]:
        if self.parse:
            self.response = self.parse(self.response)

        if self.validate:
            valid, error_msg = self.validate(self.response)
            if not valid:
                self.response = ""
        else:
            valid, error_msg = True, None

        return valid, error_msg


class InputPrompt(PromptShortcutsMixin, TextInput):
    _active: Reactive[bool] = Reactive(False)

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._SHORTCUTS_MAP["enter"] = "_teardown"

    def setup(
        self,
        name: str,
        title: str,
        callback: Optional[Callable] = None,
        parse: Optional[Callable] = None,
        validate: Optional[Callable] = None,
    ) -> None:
        self.name = name
        self.title = title

        self._callback = callback
        self._parse = parse
        self._validate = validate

        self._active = True

    async def _teardown(self) -> None:
        value = self.value
        if self._parse:
            value = self._parse(value)
        if self._validate:
            valid, error_msg = self._validate(value)
            if not valid:
                return

        if self._callback:
            await self._callback(title=self.title, value=value)
        self._active = False

    def render(self) -> Panel:
        if not self._active:
            return ""
        return super().render()


class Console(Widget):
    output: Reactive[str] = Reactive("")

    def render(self) -> Panel:
        return Panel(self.output)
