import os

from textual_pass import PASSWORD_STORE_DIR


TESTS_DIR = os.path.dirname(__file__)
TEST_STORE_DIR = os.path.join(TESTS_DIR, ".test-password-store")

if PASSWORD_STORE_DIR != TEST_STORE_DIR:
    raise OSError(
        "PASSWORD_STORE_DIR env variable not set to expected value for tests!\n"
        f"Expected path: {TEST_STORE_DIR}\nActual path: {PASSWORD_STORE_DIR}"
    )
