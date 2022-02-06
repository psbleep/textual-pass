import os
import subprocess
from typing import List

SUBPROCESS_RUN_OPTIONS = {"capture_output": True, "shell": True, "text": True}


class PasswordStore:
    def __init__(self, password_store_dir: str) -> None:
        self._password_store_dir = password_store_dir

    def search(self, search_term: str = "") -> List[str]:
        strip_length = len(self._password_store_dir) + 1
        listing = []
        for parent, _, files in os.walk(self._password_store_dir):
            listing_parent = parent[strip_length:]
            for _file in files:
                file_name, ext = os.path.splitext(_file)
                if ext == ".gpg":
                    listing_name = os.path.join(listing_parent, file_name)
                    if search_term in listing_name:
                        listing.append(listing_name)
        return sorted(listing)

    def run_shell_command(self, cmd: str) -> str:
        result = subprocess.run(cmd, **SUBPROCESS_RUN_OPTIONS)
        if result.stdout:
            stdout = f"{result.stdout}\n"
        else:
            stdout = ""
        return f"{stdout}{result.stderr}"

    def show_password(self, password: str) -> str:
        cmd = f"pass {password}"
        return self.run_shell_command(cmd)

    def show_otp(self, password: str) -> str:
        cmd = f"pass otp {password}"
        return self.run_shell_command(cmd)

    def git_pull(self) -> str:
        return self.run_shell_command("pass git pull")

    def git_push(self) -> str:
        return self.run_shell_command("pass git push")
