"""End-to-end tests for comment remover."""

import pytest
import tempfile
import shutil
from pathlib import Path
from git import Repo
from comment_remover.git_ops import ensure_at_repo_root, get_head_diff
from comment_remover.comment_detector import CommentDetector
from comment_remover.file_modifier import FileModifier


@pytest.fixture
def test_repo():
    """Create a temporary git repository for testing."""
    temp_dir = tempfile.mkdtemp()
    repo = Repo.init(temp_dir)

    repo.config_writer().set_value("user", "name", "Test User").release()
    repo.config_writer().set_value("user", "email", "test@example.com").release()

    yield Path(temp_dir), repo

    shutil.rmtree(temp_dir)


@pytest.fixture
def assets_dir():
    """Return the path to test assets directory."""
    return Path(__file__).parent / "assets"


class TestEndToEnd:
    """End-to-end tests for the comment remover."""

    def test_all_supported_languages(self, test_repo, assets_dir):
        """Test comment removal for all supported languages."""
        repo_path, repo = test_repo
        before_dir = assets_dir / "before"
        after_dir = assets_dir / "after"

        before_files = sorted(before_dir.glob("test.*"))

        for before_file in before_files:
            file_name = before_file.name
            after_file = after_dir / file_name

            assert after_file.exists(), f"Missing after file for {file_name}"

            dest_file = repo_path / file_name
            shutil.copy(before_file, dest_file)

        repo.index.add([f.name for f in before_files])
        repo.index.commit("Initial commit with clean files")

        for after_file in sorted(after_dir.glob("test.*")):
            file_name = after_file.name
            dest_file = repo_path / file_name
            shutil.copy(after_file, dest_file)

        repo.index.add([f.name for f in sorted(after_dir.glob("test.*"))])
        repo.index.commit("Add comments to files")

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(repo_path)

            validated_repo = ensure_at_repo_root()
            assert validated_repo.working_dir == str(repo_path)

            diff_text = get_head_diff(validated_repo)
            assert diff_text, "Diff should not be empty"

            detector = CommentDetector(diff_text)
            comments_by_file = detector.detect_comments()

            assert len(comments_by_file) > 0, "Should detect comments in at least one file"

            modifier = FileModifier(repo_path)
            stats = modifier.remove_comments(comments_by_file)

            assert len(stats) > 0, "Should modify at least one file"

            for file_name in stats.keys():
                result_file = repo_path / file_name
                before_file = before_dir / file_name

                result_content = result_file.read_text()
                expected_content = before_file.read_text()

                assert result_content == expected_content, (
                    f"File {file_name} content mismatch after comment removal.\n"
                    f"Expected:\n{expected_content}\n"
                    f"Got:\n{result_content}"
                )

        finally:
            os.chdir(original_cwd)

    def test_python_single_and_inline_comments(self, test_repo, assets_dir):
        """Test Python-specific comment removal."""
        repo_path, repo = test_repo

        test_file = repo_path / "example.py"
        test_file.write_text("def foo():\n    pass\n")

        repo.index.add(["example.py"])
        repo.index.commit("Initial Python file")

        test_file.write_text(
            "def foo():\n"
            "    # This is a comment\n"
            "    x = 5  # Inline comment\n"
            "    pass\n"
        )

        repo.index.add(["example.py"])
        repo.index.commit("Add Python comments")

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(repo_path)

            validated_repo = ensure_at_repo_root()
            diff_text = get_head_diff(validated_repo)

            detector = CommentDetector(diff_text)
            comments_by_file = detector.detect_comments()

            assert "example.py" in comments_by_file
            assert len(comments_by_file["example.py"]) == 2

            modifier = FileModifier(repo_path)
            modifier.remove_comments(comments_by_file)

            result = test_file.read_text()
            expected = "def foo():\n    x = 5\n    pass\n"

            assert result == expected

        finally:
            os.chdir(original_cwd)

    def test_javascript_multiline_comments(self, test_repo):
        """Test JavaScript multi-line comment removal."""
        repo_path, repo = test_repo

        test_file = repo_path / "example.js"
        test_file.write_text("function foo() {\n    return 42;\n}\n")

        repo.index.add(["example.js"])
        repo.index.commit("Initial JS file")

        test_file.write_text(
            "function foo() {\n"
            "    /* Multi-line\n"
            "       comment here */\n"
            "    return 42;\n"
            "}\n"
        )

        repo.index.add(["example.js"])
        repo.index.commit("Add multi-line comment")

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(repo_path)

            validated_repo = ensure_at_repo_root()
            diff_text = get_head_diff(validated_repo)

            detector = CommentDetector(diff_text)
            comments_by_file = detector.detect_comments()

            assert "example.js" in comments_by_file
            assert len(comments_by_file["example.js"]) == 2

            modifier = FileModifier(repo_path)
            modifier.remove_comments(comments_by_file)

            result = test_file.read_text()
            expected = "function foo() {\n    return 42;\n}\n"

            assert result == expected

        finally:
            os.chdir(original_cwd)

    def test_c_style_languages(self, test_repo):
        """Test C-style comment removal across C, C++, Java."""
        repo_path, repo = test_repo

        files_to_test = {
            "test.c": "int main() {\n    return 0;\n}\n",
            "test.java": "public class Test {\n    void run() {}\n}\n",
        }

        for filename, content in files_to_test.items():
            test_file = repo_path / filename
            test_file.write_text(content)

        repo.index.add(list(files_to_test.keys()))
        repo.index.commit("Initial C-style files")

        commented_versions = {
            "test.c": "int main() {\n    // C comment\n    return 0;  // Inline\n}\n",
            "test.java": "public class Test {\n    // Java comment\n    void run() {}  // Inline\n}\n",
        }

        for filename, content in commented_versions.items():
            test_file = repo_path / filename
            test_file.write_text(content)

        repo.index.add(list(commented_versions.keys()))
        repo.index.commit("Add C-style comments")

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(repo_path)

            validated_repo = ensure_at_repo_root()
            diff_text = get_head_diff(validated_repo)

            detector = CommentDetector(diff_text)
            comments_by_file = detector.detect_comments()

            assert len(comments_by_file) == 2

            modifier = FileModifier(repo_path)
            modifier.remove_comments(comments_by_file)

            for filename, expected_content in files_to_test.items():
                result = (repo_path / filename).read_text()
                assert result == expected_content

        finally:
            os.chdir(original_cwd)

    def test_no_comments_added(self, test_repo):
        """Test that no modifications occur when no comments are added."""
        repo_path, repo = test_repo

        test_file = repo_path / "test.py"
        test_file.write_text("def foo():\n    pass\n")

        repo.index.add(["test.py"])
        repo.index.commit("Initial commit")

        test_file.write_text("def foo():\n    x = 5\n    pass\n")

        repo.index.add(["test.py"])
        repo.index.commit("Add code without comments")

        original_cwd = Path.cwd()
        try:
            import os
            os.chdir(repo_path)

            validated_repo = ensure_at_repo_root()
            diff_text = get_head_diff(validated_repo)

            detector = CommentDetector(diff_text)
            comments_by_file = detector.detect_comments()

            assert len(comments_by_file) == 0

        finally:
            os.chdir(original_cwd)
