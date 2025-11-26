"""Language detection and comment pattern definitions."""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class CommentPattern:
    """Comment pattern definition for a language."""
    single_line: Optional[List[str]] = None
    multi_line_start: Optional[List[str]] = None
    multi_line_end: Optional[List[str]] = None


EXTENSION_TO_LANGUAGE: Dict[str, str] = {
    '.c': 'c_style',
    '.h': 'c_style',
    '.cpp': 'c_style',
    '.hpp': 'c_style',
    '.cc': 'c_style',
    '.cxx': 'c_style',
    '.java': 'c_style',
    '.js': 'c_style',
    '.jsx': 'c_style',
    '.ts': 'c_style',
    '.tsx': 'c_style',
    '.go': 'c_style',
    '.rs': 'c_style',
    '.cs': 'c_style',
    '.kt': 'c_style',
    '.swift': 'c_style',
    '.scala': 'c_style',
    '.m': 'c_style',
    '.mm': 'c_style',
    '.py': 'python',
    '.rb': 'ruby',
    '.sh': 'shell',
    '.bash': 'shell',
    '.zsh': 'shell',
    '.fish': 'shell',
    '.pl': 'perl',
    '.pm': 'perl',
    '.php': 'php',
    '.sql': 'sql',
    '.html': 'html',
    '.htm': 'html',
    '.xml': 'html',
    '.css': 'css',
    '.scss': 'css',
    '.sass': 'css',
    '.less': 'css',
    '.yaml': 'yaml',
    '.yml': 'yaml',
    '.r': 'r',
    '.R': 'r',
    '.lua': 'lua',
    '.vim': 'vim',
}


LANGUAGE_PATTERNS: Dict[str, CommentPattern] = {
    'c_style': CommentPattern(
        single_line=['//'],
        multi_line_start=['/*'],
        multi_line_end=['*/']
    ),
    'python': CommentPattern(
        single_line=['#'],
        multi_line_start=['"""', "'''"],
        multi_line_end=['"""', "'''"]
    ),
    'ruby': CommentPattern(
        single_line=['#'],
        multi_line_start=['=begin'],
        multi_line_end=['=end']
    ),
    'shell': CommentPattern(
        single_line=['#']
    ),
    'perl': CommentPattern(
        single_line=['#'],
        multi_line_start=['=pod'],
        multi_line_end=['=cut']
    ),
    'php': CommentPattern(
        single_line=['//', '#'],
        multi_line_start=['/*'],
        multi_line_end=['*/']
    ),
    'sql': CommentPattern(
        single_line=['--'],
        multi_line_start=['/*'],
        multi_line_end=['*/']
    ),
    'html': CommentPattern(
        multi_line_start=['<!--'],
        multi_line_end=['-->']
    ),
    'css': CommentPattern(
        multi_line_start=['/*'],
        multi_line_end=['*/']
    ),
    'yaml': CommentPattern(
        single_line=['#']
    ),
    'r': CommentPattern(
        single_line=['#']
    ),
    'lua': CommentPattern(
        single_line=['--'],
        multi_line_start=['--[['],
        multi_line_end=[']]']
    ),
    'vim': CommentPattern(
        single_line=['"']
    ),
}


def detect_language(filepath: str) -> Optional[str]:
    """Detect the language of a file based on its extension."""
    for ext, lang in EXTENSION_TO_LANGUAGE.items():
        if filepath.endswith(ext):
            return lang
    return None


def get_comment_pattern(language: str) -> Optional[CommentPattern]:
    """Get the comment pattern for a language."""
    return LANGUAGE_PATTERNS.get(language)
