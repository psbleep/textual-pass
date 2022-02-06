import os
import shutil
from unittest.mock import Mock

import pytest

from textual_pass.password_store import SUBPROCESS_RUN_OPTIONS, PasswordStore

from . import TEST_STORE_DIR


@pytest.fixture(autouse=True)
def use_test_store(request):
    def _cleanup():
        if os.path.exists(TEST_STORE_DIR):
            shutil.rmtree(TEST_STORE_DIR)

    _cleanup()
    request.addfinalizer(_cleanup)

    os.makedirs(TEST_STORE_DIR, exist_ok=True)
    for test_file in [
        "foo.txt",
        "a.gpg",
        "b/1.gpg",
        "b/2.gpg",
        "c/b/3.gpg",
        "c/d/4.gpg",
    ]:
        file_path = os.path.join(TEST_STORE_DIR, test_file)
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, "w") as f:
            f.write("")


@pytest.fixture
def store():
    return PasswordStore(TEST_STORE_DIR)


def test_search_returns_all_passwords_with_empty_search_term(store):
    assert store.search("") == ["a", "b/1", "b/2", "c/b/3", "c/d/4"]


def test_search_returns_only_passwords_with_search_term_when_provided(store):
    assert store.search("b") == ["b/1", "b/2", "c/b/3"]


def test_search_returns_empty_list_if_no_passwords_match_search_term(store):
    assert store.search("foobar") == []


def test_run_shell_command_runs_command_and_returns_output(mocker, store):
    mocked_subprocess_run = mocker.patch(
        "textual_pass.password_store.subprocess.run",
        return_value=Mock(stdout="hello", stderr=""),
    )
    assert store.run_shell_command("greet me") == "hello\n"
    mocked_subprocess_run.assert_called_with("greet me", **SUBPROCESS_RUN_OPTIONS)


def test_run_shell_command_returns_clean_output_when_stdout_and_stderr_both_present(
    mocker, store
):
    mocker.patch(
        "textual_pass.password_store.subprocess.run",
        return_value=Mock(stdout="hello", stderr="error: do not know your name"),
    )
    assert store.run_shell_command("greet me") == "hello\nerror: do not know your name"


def test_run_shell_command_returns_clean_output_if_no_stdout_only_stderr(mocker, store):
    mocker.patch(
        "textual_pass.password_store.subprocess.run",
        return_value=Mock(stdout="", stderr="permission denied"),
    )
    # Checking that the output is not "\npermission denied" because of blank stdout
    assert store.run_shell_command("hack fbi") == "permission denied"


def test_show_password_opens_password_in_pass_and_returns_output(store):
    store.run_shell_command = Mock(return_value="31337\n")
    assert store.show_password("hello") == "31337\n"
    store.run_shell_command.assert_called_with("pass hello")


def test_show_otp_opens_otp_in_pass_and_returns_output(store):
    store.run_shell_command = Mock(return_value="90827\n")
    assert store.show_otp("hello") == "90827\n"
    store.run_shell_command.assert_called_with("pass otp hello")


def test_git_pull_runs_git_command_in_pass(store):
    store.run_shell_command = Mock(return_value="Everything up-to-date.\n")
    assert store.git_pull() == "Everything up-to-date.\n"
    store.run_shell_command.assert_called_with("pass git pull")


def test_git_push_runs_git_command_in_pass(store):
    store.run_shell_command = Mock(return_value="Everything up-to-date.\n")
    assert store.git_push() == "Everything up-to-date.\n"
    store.run_shell_command.assert_called_with("pass git push")
