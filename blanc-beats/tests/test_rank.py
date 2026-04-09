"""Tests for the rank module (stub stage)."""

from rank import rank_variants


class TestRankStub:
    """Tests for the stubbed ranking stage."""

    def test_rank_stub_returns_empty(self):
        """Stub rank_variants returns an empty list."""
        result = rank_variants()
        assert result == []

    def test_rank_stub_prints_marker(self, capsys):
        """Stub prints [STUB] so it's obvious nothing real ran."""
        rank_variants()
        captured = capsys.readouterr()
        assert "[STUB]" in captured.out
