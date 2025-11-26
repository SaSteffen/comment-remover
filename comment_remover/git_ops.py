"""Git repository operations."""

import os
import sys
from pathlib import Path
from git import Repo, InvalidGitRepositoryError, GitCommandError
from typing import Optional


class GitValidationError(Exception):
    """Raised when git repository validation fails."""
    pass


def find_repo_root() -> Path:
    """Find the git repository root from the current directory."""
    try:
        repo = Repo(os.getcwd(), search_parent_directories=True)
        return Path(repo.working_dir)
    except InvalidGitRepositoryError:
        raise GitValidationError(
            "Not in a git repository. Please run this command from within a git repository."
        )


def validate_repo_state(repo: Repo) -> None:
    """Validate that the repository is in a valid state for comment removal."""
    if repo.is_dirty(untracked_files=True):
        dirty_files = []

        if repo.untracked_files:
            dirty_files.append(f"Untracked files: {', '.join(repo.untracked_files)}")

        changed = [item.a_path for item in repo.index.diff(None)]
        if changed:
            dirty_files.append(f"Modified files: {', '.join(changed)}")

        staged = [item.a_path for item in repo.index.diff('HEAD')]
        if staged:
            dirty_files.append(f"Staged files: {', '.join(staged)}")

        error_msg = (
            "Working directory is not clean. Please commit or stash your changes first.\n"
            + "\n".join(dirty_files)
        )
        raise GitValidationError(error_msg)


def ensure_at_repo_root() -> Repo:
    """Ensure we're at the repository root and the working tree is clean."""
    repo_root = find_repo_root()
    current_dir = Path(os.getcwd()).resolve()

    if current_dir != repo_root.resolve():
        raise GitValidationError(
            f"Must be run from repository root.\n"
            f"Current directory: {current_dir}\n"
            f"Repository root: {repo_root}\n"
            f"Please cd to {repo_root}"
        )

    repo = Repo(repo_root)
    validate_repo_state(repo)

    return repo


def get_head_diff(repo: Repo) -> str:
    """Get the diff of the HEAD commit."""
    try:
        diff_text = repo.git.show('HEAD', '--format=', '--unified=3')
        return diff_text
    except GitCommandError as e:
        raise GitValidationError(f"Failed to get HEAD commit diff: {e}")
