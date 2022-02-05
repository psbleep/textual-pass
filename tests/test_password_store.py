import os
import shutil

import pytest

from textual_pass.password_store import PasswordStore

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
