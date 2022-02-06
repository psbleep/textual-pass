import os

import pyperclip
from textual.app import App
from textual.keys import Keys
from textual.message import Message

from .password_store import PasswordStore
from .widgets import Output, Passwords, Search


def get_default_password_store_dir():
    home_dir = os.path.expanduser("~")
    return os.path.join(home_dir, ".password-store")


PASSWORD_STORE_DIR = os.getenv("PASSWORD_STORE_DIR") or get_default_password_store_dir()
store = PasswordStore(PASSWORD_STORE_DIR)


class Tpass(App):
    async def on_load(self) -> None:
        await self.bind("j", "move_focus_down")
        await self.bind("ctrl+x", "clear_search_term")
        await self.bind("k", "move_focus_up")
        await self.bind("i", "search_mode")
        await self.bind("q", "quit")

    async def action_search_mode(self) -> None:
        await self.set_search_mode()

    async def action_move_focus_up(self) -> None:
        self.passwords.focused -= 1

    async def action_move_focus_down(self) -> None:
        self.passwords.focused += 1

    async def action_clear_search_term(self) -> None:
        self.search._cursor_position = 0
        self.search.value = ""

    async def on_mount(self) -> None:
        self.search = Search(app=self, name="search", title="search: ")
        self.search.on_change_handler_name = "handle_search_on_change"

        self.passwords = Passwords(app=self)
        self.passwords.listing = store.search()

        self.output = Output()

        grid = await self.view.dock_grid(edge="left", name="left")
        grid.add_column("col", repeat=2)
        grid.add_row("top", size=3)
        grid.add_row("main")
        grid.add_areas(
            search="col1-start|col2-end,top",
            passwords="col1,main",
            output="col2,main",
        )

        grid.place(search=self.search, passwords=self.passwords, output=self.output)
        await self.set_normal_mode()

    async def handle_search_on_change(self, message: Message) -> None:
        try:
            previously_focused_password = self.passwords.get_focused_password()
        except IndexError:
            previously_focused_password = ""
        search_term = message.sender.value
        listing = store.search(search_term)
        self.passwords.listing = listing
        self.passwords.set_focus_position_to_password(previously_focused_password)

    async def set_search_mode(self) -> None:
        await self.search.focus()

    async def set_normal_mode(self) -> None:
        await self.passwords.focus()

    async def handle_key(self, key: Keys) -> None:
        if key == Keys.Enter:
            await self.open_password()
            await self.set_normal_mode()
        elif key in (Keys.Up, Keys.ControlK):
            await self.action_move_focus_up()
        elif key in (Keys.Down, Keys.ControlJ):
            await self.action_move_focus_down()
        elif key == Keys.ControlO:
            await self.open_password(otp=True, clip=True)
            await self.set_normal_mode()
        elif key == Keys.ControlS:
            await self.sync_store()
        elif key == Keys.ControlY:
            await self.open_password(clip=True)
            await self.set_normal_mode()
        elif key == Keys.ControlQ:
            await self.action_quit()
        elif key == Keys.Escape:
            await self.set_normal_mode()

    async def sync_store(self) -> None:
        pull_output = store.git_pull()
        push_output = store.git_push()
        self.output.output = f"{pull_output}\n{push_output}"

    async def open_password(self, otp=False, clip=False) -> None:
        try:
            password = self.passwords.get_focused_password()
        except IndexError:
            return

        if otp:
            output = store.show_otp(password)
        else:
            output = store.show_password(password)

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

        self.output.output = output
