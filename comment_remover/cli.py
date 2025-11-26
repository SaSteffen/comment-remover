"""CLI entry point for comment remover."""

import sys
from pathlib import Path
from .git_ops import ensure_at_repo_root, get_head_diff, GitValidationError
from .comment_detector import CommentDetector
from .file_modifier import FileModifier


def main():
    """Main CLI entry point."""
    try:
        print("🔍 Validating git repository state...")
        repo = ensure_at_repo_root()
        repo_root = Path(repo.working_dir)

        print("✅ Repository validation passed")
        print(f"   Repository root: {repo_root}")

        print("\n📄 Extracting HEAD commit diff...")
        diff_text = get_head_diff(repo)

        if not diff_text:
            print("ℹ️  No changes found in HEAD commit")
            return 0

        print("✅ Diff extracted")

        print("\n🔎 Detecting comments in added lines...")
        detector = CommentDetector(diff_text)
        comments_by_file = detector.detect_comments()

        if not comments_by_file:
            print("ℹ️  No comments detected in the changes")
            return 0

        total_comments = sum(len(comments) for comments in comments_by_file.values())
        print(f"✅ Found {total_comments} comment line(s) across {len(comments_by_file)} file(s)")

        for filepath, comments in comments_by_file.items():
            print(f"   {filepath}: {len(comments)} comment(s)")

        print("\n✂️  Removing comments from files...")
        modifier = FileModifier(repo_root)
        stats = modifier.remove_comments(comments_by_file)

        total_modified = sum(stats.values())
        print(f"✅ Removed {total_modified} comment line(s)")

        for filepath, count in stats.items():
            print(f"   {filepath}: {count} line(s) removed/modified")

        print("\n✨ Done! Files have been modified.")
        print("   Review the changes with: git diff")
        print("   Stage them with: git add <files>")

        return 0

    except GitValidationError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
