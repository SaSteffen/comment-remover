"""Tests for file_modifier module."""

import pytest
import tempfile
from pathlib import Path
from comment_remover.file_modifier import FileModifier
from comment_remover.comment_detector import CommentLine


class TestFileModifier:
    """Tests for FileModifier class."""

    def test_remove_single_line_comment(self, tmp_path):
        """Test removal of a single-line comment."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def foo():\n    # comment\n    pass\n")

        comments = [
            CommentLine(
                filepath="test.py",
                line_number=2,
                content="    # comment\n",
                is_inline=False,
            )
        ]

        modifier = FileModifier(tmp_path)
        stats = modifier.remove_comments({"test.py": comments})

        result = test_file.read_text()
        assert result == "def foo():\n    pass\n"
        assert stats["test.py"] == 1

    def test_remove_inline_comment(self, tmp_path):
        """Test removal of an inline comment."""
        test_file = tmp_path / "test.py"
        test_file.write_text("def foo():\n    x = 5  # inline\n    pass\n")

        comments = [
            CommentLine(
                filepath="test.py",
                line_number=2,
                content="    x = 5  # inline\n",
                is_inline=True,
            )
        ]

        modifier = FileModifier(tmp_path)
        stats = modifier.remove_comments({"test.py": comments})

        result = test_file.read_text()
        assert result == "def foo():\n    x = 5\n    pass\n"
        assert stats["test.py"] == 1

    def test_remove_multiple_comments(self, tmp_path):
        """Test removal of multiple comments."""
        test_file = tmp_path / "test.py"
        test_file.write_text(
            "def foo():\n    # comment 1\n    x = 5\n    # comment 2\n    pass\n"
        )

        comments = [
            CommentLine(
                filepath="test.py",
                line_number=2,
                content="    # comment 1\n",
                is_inline=False,
            ),
            CommentLine(
                filepath="test.py",
                line_number=4,
                content="    # comment 2\n",
                is_inline=False,
            ),
        ]

        modifier = FileModifier(tmp_path)
        stats = modifier.remove_comments({"test.py": comments})

        result = test_file.read_text()
        assert result == "def foo():\n    x = 5\n    pass\n"
        assert stats["test.py"] == 2

    def test_file_not_found(self, tmp_path, capsys):
        """Test handling of non-existent file."""
        comments = [
            CommentLine(
                filepath="nonexistent.py",
                line_number=1,
                content="# comment\n",
                is_inline=False,
            )
        ]

        modifier = FileModifier(tmp_path)
        stats = modifier.remove_comments({"nonexistent.py": comments})

        captured = capsys.readouterr()
        assert "does not exist" in captured.out
        assert "nonexistent.py" not in stats

    def test_remove_c_style_comments(self, tmp_path):
        """Test removal of C-style comments."""
        test_file = tmp_path / "test.js"
        test_file.write_text("function foo() {\n    // comment\n    return 42;\n}\n")

        comments = [
            CommentLine(
                filepath="test.js",
                line_number=2,
                content="    // comment\n",
                is_inline=False,
            )
        ]

        modifier = FileModifier(tmp_path)
        stats = modifier.remove_comments({"test.js": comments})

        result = test_file.read_text()
        assert result == "function foo() {\n    return 42;\n}\n"

    def test_preserve_non_comment_lines(self, tmp_path):
        """Test that non-comment lines are preserved."""
        test_file = tmp_path / "test.py"
        original_content = "def foo():\n    x = 5\n    # comment\n    y = 10\n    return x + y\n"
        test_file.write_text(original_content)

        comments = [
            CommentLine(
                filepath="test.py",
                line_number=3,
                content="    # comment\n",
                is_inline=False,
            )
        ]

        modifier = FileModifier(tmp_path)
        modifier.remove_comments({"test.py": comments})

        result = test_file.read_text()
        assert result == "def foo():\n    x = 5\n    y = 10\n    return x + y\n"
