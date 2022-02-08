import pyperclip
from textual.app import App as TextualApp
from textual.message import Message

from . import PASSWORD_STORE_DIR
from .password_store import PasswordStore
from .widgets import Console, Passwords, Search


class App(TextualApp):
    async def on_mount(self) -> None:
        self._store = PasswordStore(PASSWORD_STORE_DIR)

        self._search = Search(name="search", title="search: ")
        self._search.on_change_handler_name = "handle_search_on_change"

        self._passwords = Passwords()
        self._passwords.listing = self._store.search()

        self._console = Console()

        grid = await self.view.dock_grid(edge="left", name="left")
        grid.add_column("col", repeat=2)
        grid.add_row("top", size=3)
        grid.add_row("main")
        grid.add_areas(
            search="col1-start|col2-end,top",
            passwords="col1,main",
            console="col2,main",
        )

        grid.place(
            search=self._search, passwords=self._passwords, console=self._console
        )
        await self.set_normal_mode()

    async def handle_search_on_change(self, message: Message) -> None:
        try:
            previously_focused_password = self._passwords.get_focused_password()
        except IndexError:
            previously_focused_password = ""
        search_term = message.sender.value
        listing = self._store.search(search_term)
        self._passwords.listing = listing
        self._passwords.set_focused_position_to_password(previously_focused_password)

    async def on_load(self) -> None:
        await self.bind("j,down", "move_focus_down")
        await self.bind("k,up", "move_focus_up")
        await self.bind("i", "search_mode")
        await self.bind("q,ctrl+q", "quit")
        await self.bind("ctrl+o", "open_password('otp','clip')")
        await self.bind("ctrl+s", "sync_store")
        await self.bind("ctrl+x", "clear_search_term")
        await self.bind("ctrl+y", "open_password('','clip')")
        await self.bind("escape", "normal_mode")
        await self.bind("enter", "open_password")

    async def action_search_mode(self) -> None:
        await self.set_search_mode()

    async def action_normal_mode(self) -> None:
        await self.set_normal_mode()

    async def action_move_focus_up(self) -> None:
        self._passwords.focused_position -= 1

    async def action_move_focus_down(self) -> None:
        self._passwords.focused_position += 1

    async def action_clear_search_term(self) -> None:
        self._search.cursor_position = 0
        self._search.value = ""
        self._passwords.listing = self._store.search()

    async def action_sync_store(self) -> None:
        pull_output = self._store.git_pull()
        push_output = self._store.git_push()
        self._console.output = f"{pull_output}\n{push_output}"

    async def action_open_password(self, otp: str = "", clip: str = "") -> None:
        try:
            password = self._passwords.get_focused_password()
        except IndexError:
            return

        if otp:
            output = self._store.show_otp(password)
        else:
            output = self._store.show_password(password)

        if clip:
            password_value, *other = output.splitlines()
            other = "\n".join(other)
            if password_value:
                pyperclip.copy(password_value)
                if otp:
                    otp_msg = "OTP code for "
                else:
                    otp_msg = ""
                output = f"Copied {otp_msg}{password} to clipboard.\n{other}"
            else:
                output = other

        self._console.output = output
        await self.set_normal_mode()

    async def set_search_mode(self) -> None:
        await self._search.focus()

    async def set_normal_mode(self) -> None:
        await self._passwords.focus()
