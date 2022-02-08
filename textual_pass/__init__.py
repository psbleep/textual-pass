import os


def get_default_password_store_dir():
    home_dir = os.path.expanduser("~")
    return os.path.join(home_dir, ".password-store")


PASSWORD_STORE_DIR = os.path.abspath(
    os.getenv("PASSWORD_STORE_DIR") or get_default_password_store_dir()
)
