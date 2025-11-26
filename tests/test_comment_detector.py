"""Tests for comment_detector module."""

import pytest
from comment_remover.comment_detector import CommentDetector, CommentLine


class TestCommentDetector:
    """Tests for CommentDetector class."""

    def test_detect_single_line_comment_python(self):
        """Test detection of single-line Python comment."""
        diff = """--- a/test.py
+++ b/test.py
@@ -1,2 +1,3 @@
 def foo():
+    # This is a comment
     pass
"""
        detector = CommentDetector(diff)
        comments = detector.detect_comments()

        assert "test.py" in comments
        assert len(comments["test.py"]) == 1
        assert comments["test.py"][0].line_number == 2
        assert not comments["test.py"][0].is_inline

    def test_detect_inline_comment_python(self):
        """Test detection of inline Python comment."""
        diff = """--- a/test.py
+++ b/test.py
@@ -1,2 +1,3 @@
 def foo():
+    x = 5  # inline comment
     pass
"""
        detector = CommentDetector(diff)
        comments = detector.detect_comments()

        assert "test.py" in comments
        assert len(comments["test.py"]) == 1
        assert comments["test.py"][0].is_inline

    def test_detect_c_style_single_line_comment(self):
        """Test detection of C-style single-line comment."""
        diff = """--- a/test.js
+++ b/test.js
@@ -1,3 +1,4 @@
 function foo() {
+    // This is a comment
     return 42;
 }
"""
        detector = CommentDetector(diff)
        comments = detector.detect_comments()

        assert "test.js" in comments
        assert len(comments["test.js"]) == 1

    def test_detect_multiline_comment_c_style(self):
        """Test detection of multi-line C-style comment."""
        diff = """--- a/test.js
+++ b/test.js
@@ -1,3 +1,6 @@
 function foo() {
+    /*
+     * Multi-line comment
+     */
     return 42;
 }
"""
        detector = CommentDetector(diff)
        comments = detector.detect_comments()

        assert "test.js" in comments
        assert len(comments["test.js"]) == 3

    def test_ignore_code_lines(self):
        """Test that non-comment code lines are ignored."""
        diff = """--- a/test.py
+++ b/test.py
@@ -1,2 +1,4 @@
 def foo():
+    x = 5
+    y = 10
     pass
"""
        detector = CommentDetector(diff)
        comments = detector.detect_comments()

        assert "test.py" not in comments

    def test_detect_comments_in_multiple_files(self):
        """Test detection of comments across multiple files."""
        diff = """--- a/test.py
+++ b/test.py
@@ -1,2 +1,3 @@
 def foo():
+    # Comment in Python
     pass
--- a/test.js
+++ b/test.js
@@ -1,2 +1,3 @@
 function bar() {
+    // Comment in JS
     return 1;
 }
"""
        detector = CommentDetector(diff)
        comments = detector.detect_comments()

        assert len(comments) == 2
        assert "test.py" in comments
        assert "test.js" in comments

    def test_ignore_comment_in_string(self):
        """Test that comments inside strings are not detected."""
        diff = """--- a/test.py
+++ b/test.py
@@ -1,2 +1,3 @@
 def foo():
+    url = "http://example.com"
     pass
"""
        detector = CommentDetector(diff)
        comments = detector.detect_comments()

        assert "test.py" not in comments

    def test_no_comments_in_diff(self):
        """Test diff with no comments."""
        diff = """--- a/test.py
+++ b/test.py
@@ -1,2 +1,4 @@
 def foo():
+    x = 1
+    return x
     pass
"""
        detector = CommentDetector(diff)
        comments = detector.detect_comments()

        assert len(comments) == 0
