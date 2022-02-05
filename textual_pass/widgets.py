from typing import List

from rich.panel import Panel
from textual.events import Event
from textual.reactive import Reactive
from textual.widget import Widget
from textual_inputs import TextInput


class Search(TextInput):
    def __init__(self, app, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._app = app

    async def on_key(self, event: Event) -> None:
        await self._app.handle_key(event.key)


class Passwords(Widget):
    focused: Reactive[int] = Reactive(0)
    listing: Reactive[List[str]] = Reactive([])

    def __init__(self, app, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._app = app

    def render(self) -> Panel:
        self.focused = self._get_focused(self.focused)
        output_lines = self._get_output_lines()
        return Panel("\n".join(output_lines))

    def _get_focused(self, focused: int) -> int:
        if focused < 0:
            return 0

        max_idx = len(self.listing) - 1
        return min([max_idx, focused])

    def _get_output_lines(self) -> List[str]:
        output_lines = []
        for idx, line in enumerate(self.listing):
            if idx == self.focused:
                line = f"[bold]{line}[/bold]"
            output_lines.append(line)
        return output_lines

    async def on_key(self, event: Event) -> None:
        await self._app.handle_key(event.key)

    def get_focused_password(self) -> str:
        return self.listing[self.focused]


class Output(Widget):
    output: Reactive[str] = Reactive("")

    def render(self) -> Panel:
        return Panel(self.output)
