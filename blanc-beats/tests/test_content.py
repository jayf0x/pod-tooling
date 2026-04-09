"""Tests for the content module (stub stage)."""

from content import generate_description, generate_cover


class TestContentStub:
    """Tests for the stubbed content stage."""

    def test_describe_stub_returns_string(self):
        """Stub generate_description returns a placeholder string."""
        result = generate_description("chill lo-fi beat")
        assert isinstance(result, str)
        assert "[STUB]" in result

    def test_describe_stub_prints_marker(self, capsys):
        """Stub prints [STUB] so it's obvious nothing real ran."""
        generate_description("test")
        captured = capsys.readouterr()
        assert "[STUB]" in captured.out

    def test_cover_stub_returns_none(self):
        """Stub generate_cover returns None."""
        result = generate_cover("test cover")
        assert result is None

    def test_cover_stub_prints_marker(self, capsys):
        """Stub prints [STUB] so it's obvious nothing real ran."""
        generate_cover("test")
        captured = capsys.readouterr()
        assert "[STUB]" in captured.out
