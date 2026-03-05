"""Shared runtime state for CLI and processing pipeline coordination."""


class RuntimeState:
    """Process-wide mutable runtime settings."""

    def __init__(self) -> None:
        # Keep user-visible default behavior unchanged.
        self.mode = "auto"


runtime_state = RuntimeState()
