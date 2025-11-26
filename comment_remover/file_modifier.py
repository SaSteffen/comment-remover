"""File modification logic for removing comments."""

import os
from pathlib import Path
from typing import List, Dict
from .comment_detector import CommentLine


class FileModifier:
    """Modifies files to remove detected comments."""

    def __init__(self, repo_root: Path):
        """Initialize with repository root."""
        self.repo_root = repo_root

    def remove_comments(self, comments_by_file: Dict[str, List[CommentLine]]) -> Dict[str, int]:
        """
        Remove comments from files.

        Args:
            comments_by_file: Dictionary mapping file paths to lists of CommentLine objects.

        Returns:
            Dictionary with statistics: file paths to number of lines removed.
        """
        stats = {}

        for filepath, comments in comments_by_file.items():
            full_path = self.repo_root / filepath

            if not full_path.exists():
                print(f"Warning: File {filepath} does not exist, skipping.")
                continue

            lines_removed = self._remove_comments_from_file(full_path, comments)
            stats[filepath] = lines_removed

        return stats

    def _remove_comments_from_file(self, file_path: Path, comments: List[CommentLine]) -> int:
        """
        Remove specific comment lines from a file.

        Args:
            file_path: Path to the file.
            comments: List of CommentLine objects to remove.

        Returns:
            Number of lines removed/modified.
        """
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()

        original_line_count = len(lines)
        lines_to_remove = set()
        lines_to_modify = {}

        for comment in comments:
            line_idx = comment.line_number - 1

            if line_idx < 0 or line_idx >= len(lines):
                continue

            if comment.is_inline:
                lines_to_modify[line_idx] = self._remove_inline_comment(
                    lines[line_idx], comment.content
                )
            else:
                lines_to_remove.add(line_idx)

        new_lines = []
        for idx, line in enumerate(lines):
            if idx in lines_to_remove:
                continue
            elif idx in lines_to_modify:
                new_lines.append(lines_to_modify[idx])
            else:
                new_lines.append(line)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)

        modifications_count = len(lines_to_remove) + len(lines_to_modify)
        return modifications_count

    def _remove_inline_comment(self, line: str, original_line: str) -> str:
        """
        Remove inline comment from a line.

        Handles both single-line markers (//, #, --) and inline multi-line markers (/* */).
        """
        single_line_markers = ['//', '#', '--']

        for marker in single_line_markers:
            marker_idx = line.find(marker)

            if marker_idx == -1:
                continue

            before_marker = line[:marker_idx]

            if self._is_in_string(before_marker):
                continue

            cleaned = before_marker.rstrip()

            if line.endswith('\n'):
                cleaned += '\n'

            return cleaned

        start_marker = '/*'
        end_marker = '*/'
        start_idx = line.find(start_marker)

        if start_idx != -1:
            before_comment = line[:start_idx]

            if not self._is_in_string(before_comment):
                end_idx = line.find(end_marker, start_idx)

                if end_idx != -1:
                    after_comment = line[end_idx + len(end_marker):]
                    cleaned = before_comment.rstrip() + after_comment.lstrip()

                    if cleaned and not cleaned.endswith('\n') and line.endswith('\n'):
                        cleaned += '\n'

                    return cleaned

        return line

    def _is_in_string(self, text: str) -> bool:
        """
        Heuristic check if the position is inside a string literal.
        """
        single_quotes = text.count("'") - text.count("\\'")
        double_quotes = text.count('"') - text.count('\\"')

        return (single_quotes % 2 == 1) or (double_quotes % 2 == 1)
