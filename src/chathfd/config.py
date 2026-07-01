"Typed environment configuration for ChatHFD."

from chatenv import BaseEnvConfig, EnvField


class ChathfdConfig(BaseEnvConfig):
    "ChatHFD ChatEnv configuration."

    _title = "ChatHFD Configuration"
    _aliases = ["chathfd"]
    _storage_dir = "Chathfd"

    @classmethod
    def test(cls) -> None:
        """Validate schema registration without external side effects."""

        print(f"Testing {cls._title}...")
        print("Schema loaded; no network test is required.")

    CHATHFD_API_KEY = EnvField(
        "CHATHFD_API_KEY",
        desc="API key",
        is_sensitive=True,
    )


__all__ = ["ChathfdConfig"]
