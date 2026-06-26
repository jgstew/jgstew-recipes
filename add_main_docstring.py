#!/usr/bin/env python3
"""Pre-commit hook: add a boilerplate docstring to named functions when missing or empty.

Usage (standalone):
    add_main_docstring.py [options] <file.py|directory> [...]

Usage (pre-commit, files injected automatically):
    see .pre-commit-hooks.yaml / .pre-commit-config.yaml

Options:
    -f, --functions   Comma-separated function names to check  [default: main]
    -d, --docstring   Boilerplate text to insert               [default: Execution starts here.]

Exit codes:
    0  Nothing changed
    1  One or more files were modified (pre-commit will abort the commit so the
       user can re-stage the updated files)
"""

import argparse
import ast
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

DEFAULT_FUNCTIONS = "main"
DEFAULT_DOCSTRING = "Execution starts here."

SKIP_PARTS = {"site-packages", "venv", "virtualenv"}


def find_functions_without_docstring(source, function_names):
    """Locate named functions missing a non-empty docstring.

    Args:
        source: Python source code as a string
        function_names: Set of function names to check

    Returns:
        List of (def_lineno, body_col_offset) tuples (1-based line numbers).
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    results = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name not in function_names:
            continue
        if not node.body:
            continue
        first = node.body[0]
        has_docstring = (
            isinstance(first, ast.Expr)
            and isinstance(first.value, ast.Constant)
            and isinstance(first.value.value, str)
            and first.value.value.strip()
        )
        if not has_docstring:
            # Use node.lineno (the def line) rather than node.body[0].lineno so
            # that comments sitting between the def and the first real statement
            # don't push the docstring below them.
            results.append((node.lineno, node.col_offset + 4))
    return results


def _find_def_end(lines, def_lineno):
    """Return the 0-based index of the line that closes the def signature (the ':' line).

    Args:
        lines: List of source lines (with line endings)
        def_lineno: 1-based line number where the def keyword appears

    Returns:
        0-based index of the closing ':' line
    """
    idx = def_lineno - 1
    while idx < len(lines):
        code = lines[idx].split("#")[0].rstrip()
        if code.endswith(":"):
            return idx
        idx += 1
    return def_lineno - 1  # fallback


def add_docstring(filepath, function_names, docstring):
    """Insert the boilerplate docstring into named functions that lack one.

    Args:
        filepath: Path to the Python file to update
        function_names: Set of function names to check
        docstring: Boilerplate text to insert (without quotes)

    Returns:
        True if the file was modified, False otherwise
    """
    path = Path(filepath)
    source = path.read_text(encoding="utf-8")
    lines = source.splitlines(keepends=True)

    targets = find_functions_without_docstring(source, function_names)
    if not targets:
        return False

    # Process in reverse order so earlier insertions don't shift later line numbers
    for def_lineno, col_offset in sorted(targets, reverse=True):
        sig_end_idx = _find_def_end(lines, def_lineno)
        indent = " " * col_offset
        docstring_line = f'{indent}"""{docstring}"""\n'
        lines.insert(sig_end_idx + 1, docstring_line)

    path.write_text("".join(lines), encoding="utf-8")
    return True


def _iter_py_files(directory):
    """Yield .py files under directory, skipping hidden and virtual-env folders.

    Args:
        directory: Root Path to search

    Yields:
        Path objects for each eligible .py file
    """
    for path in sorted(directory.rglob("*.py")):
        if any(part.startswith(".") or part in SKIP_PARTS for part in path.parts):
            continue
        yield path


def main():
    """Execution starts here."""
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help="Python files or directories to process",
    )
    parser.add_argument(
        "-f",
        "--functions",
        default=DEFAULT_FUNCTIONS,
        metavar="NAMES",
        help=f"Comma-separated function names to check (default: {DEFAULT_FUNCTIONS!r})",
    )
    parser.add_argument(
        "-d",
        "--docstring",
        default=DEFAULT_DOCSTRING,
        metavar="TEXT",
        help=f"Boilerplate docstring text (default: {DEFAULT_DOCSTRING!r})",
    )
    args = parser.parse_args()

    if not args.files:
        parser.print_help()
        sys.exit(0)

    function_names = {name.strip() for name in args.functions.split(",")}
    docstring_text = args.docstring

    py_files = []
    for arg in args.files:
        target = Path(arg)
        if target.is_dir():
            py_files.extend(_iter_py_files(target))
        elif target.suffix == ".py":
            py_files.append(target)
        else:
            print(f"Skipping non-Python file: {target}", file=sys.stderr)

    changed = 0
    with ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(add_docstring, f, function_names, docstring_text): f
            for f in py_files
        }
        for future in as_completed(futures):
            f = futures[future]
            try:
                if future.result():
                    print(f"Updated: {f}")
                    changed += 1
            except Exception as exc:
                print(f"Error processing {f}: {exc}", file=sys.stderr)

    if changed:
        print(f"\n{changed} file(s) updated — re-stage and commit again.")
        sys.exit(1)


if __name__ == "__main__":
    main()
