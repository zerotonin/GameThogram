from .key_bindings import KeyBindings


class ScorerAction:
    """Base class for any action that can be bound to a button.

    Used for both behaviours and movie control actions (play,
    pause, seek, etc.). Stores per-device key bindings.
    """

    def __init__(self, name: str, icon_path: str = None):
        self.key_bindings = KeyBindings()
        self._name = name
        self.icon_path = icon_path

    @property
    def name(self) -> str:
        return self._name

    def set_name(self, s: str):
        self._name = s
