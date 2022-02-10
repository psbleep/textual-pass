from .app import TPassApp


def main():
    app = TPassApp()
    app.run(title="TPass", log="textual.log")


if __name__ == "__main__":
    main()
