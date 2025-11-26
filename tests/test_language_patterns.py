"""Tests for language_patterns module."""

import pytest
from comment_remover.language_patterns import (
    detect_language,
    get_comment_pattern,
    CommentPattern,
)


class TestLanguageDetection:
    """Tests for language detection."""

    def test_detect_c_style_languages(self):
        """Test detection of C-style languages."""
        assert detect_language("test.c") == "c_style"
        assert detect_language("test.cpp") == "c_style"
        assert detect_language("test.java") == "c_style"
        assert detect_language("test.js") == "c_style"
        assert detect_language("test.ts") == "c_style"
        assert detect_language("test.go") == "c_style"
        assert detect_language("test.rs") == "c_style"

    def test_detect_python(self):
        """Test detection of Python."""
        assert detect_language("test.py") == "python"

    def test_detect_shell(self):
        """Test detection of shell scripts."""
        assert detect_language("test.sh") == "shell"
        assert detect_language("test.bash") == "shell"

    def test_detect_unknown_extension(self):
        """Test detection of unknown file extension."""
        assert detect_language("test.unknown") is None
        assert detect_language("test.xyz") is None

    def test_detect_no_extension(self):
        """Test detection of file without extension."""
        assert detect_language("Makefile") is None


class TestCommentPatterns:
    """Tests for comment pattern retrieval."""

    def test_get_c_style_pattern(self):
        """Test C-style comment pattern."""
        pattern = get_comment_pattern("c_style")
        assert pattern is not None
        assert "//" in pattern.single_line
        assert "/*" in pattern.multi_line_start
        assert "*/" in pattern.multi_line_end

    def test_get_python_pattern(self):
        """Test Python comment pattern."""
        pattern = get_comment_pattern("python")
        assert pattern is not None
        assert "#" in pattern.single_line
        assert '"""' in pattern.multi_line_start
        assert "'''" in pattern.multi_line_start

    def test_get_unknown_language(self):
        """Test getting pattern for unknown language."""
        assert get_comment_pattern("unknown_lang") is None
