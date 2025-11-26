# Comment Remover

Automatically remove comments that were added in the latest git commit.

## Installation

```bash
poetry install
```

## Usage

Run from the root of your git repository:

```bash
poetry run remove-comments
```

Or install the package and use directly:

```bash
poetry build
pip install dist/comment_remover-*.whl
remove-comments
```

## Requirements

- Must be run from the root of a git repository
- Working tree must be clean (no staged or modified files)
- Operates on the HEAD commit

## Supported Languages

The tool supports comment detection for 20+ programming languages including:

- C/C++, C#, Java
- JavaScript, TypeScript
- Python, Ruby, PHP
- Go, Rust, Swift, Kotlin, Scala
- Shell scripts (Bash, Zsh, Fish)
- SQL, HTML, CSS
- YAML, Perl, R, Lua, Vim

## How It Works

1. Validates git repository state
2. Extracts the diff from the HEAD commit
3. Identifies comment lines that were added
4. Removes those comments from the files
5. Leaves modified files unstaged for review

## Development

Run tests:

```bash
poetry run pytest
```
