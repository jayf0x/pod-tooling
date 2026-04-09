"""Tests for the post module (stub stage)."""

from post import upload_to_youtube


class TestPostStub:
    """Tests for the stubbed posting stage."""

    def test_post_stub_returns_dict(self):
        """Stub upload_to_youtube returns a dry-run dict."""
        result = upload_to_youtube()
        assert isinstance(result, dict)
        assert result["dry_run"] is True

    def test_post_stub_prints_marker(self, capsys):
        """Stub prints [STUB] so it's obvious nothing real ran."""
        upload_to_youtube()
        captured = capsys.readouterr()
        assert "[STUB]" in captured.out
