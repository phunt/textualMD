from textual.app import App, ComposeResult
from textual.widgets import Header, Footer

class DarkApp(App):
    """A simple Textual app with dark mode toggle."""
    
    CSS = """
    Screen {
        background: $surface;
        color: $text;
    }
    """

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("q", "quit", "Quit")
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()

    def action_toggle_dark(self) -> None:
        """Toggle dark mode."""
        # In Textual 5.0.1, we use the theme attribute
        self.theme = "textual-dark" if self.theme == "textual-light" else "textual-light"

if __name__ == "__main__":
    app = DarkApp()
    app.run() 