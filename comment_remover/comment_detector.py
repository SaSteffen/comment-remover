"""Comment detection logic."""

import re
from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
from unidiff import PatchSet
from .language_patterns import detect_language, get_comment_pattern, CommentPattern


@dataclass
class CommentLine:
    """Represents a comment line to be removed."""
    filepath: str
    line_number: int
    content: str
    is_inline: bool = False


class CommentDetector:
    """Detects comments in git diff."""

    def __init__(self, diff_text: str):
        """Initialize with diff text."""
        self.diff_text = diff_text
        self.patch_set = PatchSet(diff_text)

    def detect_comments(self) -> Dict[str, List[CommentLine]]:
        """
        Detect all comments that were added in the diff.

        Returns:
            Dictionary mapping file paths to lists of CommentLine objects.
        """
        comments_by_file: Dict[str, List[CommentLine]] = {}

        for patched_file in self.patch_set:
            if not patched_file.is_added_file and not patched_file.is_modified_file:
                continue

            filepath = patched_file.path
            language = detect_language(filepath)

            if not language:
                continue

            pattern = get_comment_pattern(language)
            if not pattern:
                continue

            file_comments = self._detect_comments_in_file(
                patched_file, filepath, pattern
            )

            if file_comments:
                comments_by_file[filepath] = file_comments

        return comments_by_file

    def _detect_comments_in_file(
        self, patched_file, filepath: str, pattern: CommentPattern
    ) -> List[CommentLine]:
        """Detect comments in a single file from the diff."""
        comments = []
        in_multiline_comment = False
        multiline_start_marker = None

        for hunk in patched_file:
            for line in hunk:
                if not line.is_added:
                    continue

                line_content = line.value
                target_line_no = line.target_line_no

                if pattern.multi_line_start and pattern.multi_line_end:
                    multiline_result = self._check_multiline_comment(
                        line_content,
                        pattern,
                        in_multiline_comment,
                        multiline_start_marker,
                    )

                    if multiline_result['is_comment']:
                        comments.append(
                            CommentLine(
                                filepath=filepath,
                                line_number=target_line_no,
                                content=line_content,
                                is_inline=multiline_result.get('is_inline', False),
                            )
                        )

                    in_multiline_comment = multiline_result['in_multiline']
                    multiline_start_marker = multiline_result.get('start_marker')

                    if multiline_result['is_comment']:
                        continue

                if pattern.single_line:
                    single_line_result = self._check_single_line_comment(
                        line_content, pattern
                    )

                    if single_line_result:
                        comments.append(
                            CommentLine(
                                filepath=filepath,
                                line_number=target_line_no,
                                content=line_content,
                                is_inline=single_line_result['is_inline'],
                            )
                        )

        return comments

    def _check_multiline_comment(
        self,
        line: str,
        pattern: CommentPattern,
        currently_in_multiline: bool,
        current_start_marker: Optional[str],
    ) -> Dict:
        """
        Check if a line is part of a multi-line comment.

        Returns a dict with:
        - is_comment: bool
        - in_multiline: bool (state after processing this line)
        - start_marker: str or None (which marker started the comment)
        """
        stripped = line.strip()

        if currently_in_multiline:
            is_end = False
            for end_marker in pattern.multi_line_end:
                if current_start_marker and pattern.multi_line_start:
                    start_idx = pattern.multi_line_start.index(current_start_marker)
                    if start_idx < len(pattern.multi_line_end):
                        if end_marker == pattern.multi_line_end[start_idx]:
                            if end_marker in stripped:
                                is_end = True
                                break
                elif end_marker in stripped:
                    is_end = True
                    break

            if is_end:
                return {
                    'is_comment': True,
                    'in_multiline': False,
                    'start_marker': None,
                    'is_inline': False,
                }
            else:
                return {
                    'is_comment': True,
                    'in_multiline': True,
                    'start_marker': current_start_marker,
                    'is_inline': False,
                }

        for i, start_marker in enumerate(pattern.multi_line_start):
            if start_marker in stripped:
                end_marker = pattern.multi_line_end[i] if i < len(pattern.multi_line_end) else pattern.multi_line_end[0]

                if end_marker in stripped:
                    start_idx = stripped.find(start_marker)
                    before_comment = stripped[:start_idx].strip()
                    is_inline = len(before_comment) > 0

                    return {
                        'is_comment': True,
                        'in_multiline': False,
                        'start_marker': None,
                        'is_inline': is_inline,
                    }
                else:
                    return {
                        'is_comment': True,
                        'in_multiline': True,
                        'start_marker': start_marker,
                        'is_inline': False,
                    }

        return {
            'is_comment': False,
            'in_multiline': False,
            'start_marker': None,
            'is_inline': False,
        }

    def _check_single_line_comment(
        self, line: str, pattern: CommentPattern
    ) -> Optional[Dict]:
        """
        Check if a line is a single-line comment or has an inline comment.

        Returns None if not a comment, or a dict with:
        - is_inline: bool
        """
        stripped = line.strip()

        if not stripped:
            return None

        for marker in pattern.single_line:
            marker_idx = stripped.find(marker)

            if marker_idx == -1:
                continue

            if marker_idx == 0:
                return {'is_inline': False}

            before_marker = stripped[:marker_idx]

            if self._is_in_string(before_marker):
                continue

            if before_marker.strip():
                return {'is_inline': True}
            else:
                return {'is_inline': False}

        return None

    def _is_in_string(self, text: str) -> bool:
        """
        Heuristic check if the position is inside a string literal.

        This is a simple heuristic that counts quotes.
        """
        single_quotes = text.count("'") - text.count("\\'")
        double_quotes = text.count('"') - text.count('\\"')

        return (single_quotes % 2 == 1) or (double_quotes % 2 == 1)
