#!/usr/bin/env python3
"""Add a boilerplate docstring to main() methods that are missing one or have an empty one."""

import ast
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

DOCSTRING = "Execution starts here."


def find_mains_without_docstring(source):
    """Locate main() functions missing a non-empty docstring.

    Args:
        source: Python source code as a string

    Returns:
        List of (def_lineno, body_col_offset) tuples for main() functions needing a docstring.
        def_lineno is 1-based; body_col_offset is the indentation of the body in spaces.
    """
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return []

    results = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if node.name != "main":
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
            # Return the def line and the expected body indentation.
            # Do NOT use node.body[0].lineno — ast ignores comments, so that
            # lineno may be below comments that sit between the def and the
            # first real statement.  We scan for the signature's closing ":"
            # in add_docstring instead.
            results.append((node.lineno, node.col_offset + 4))
    return results


def _find_def_end(lines, def_lineno):
    """Return the 0-based index of the line that ends the def signature (the ':' line).

    Args:
        lines: List of source lines (with line endings)
        def_lineno: 1-based line number where the def keyword appears

    Returns:
        0-based index of the closing ':' line
    """
    idx = def_lineno - 1
    while idx < len(lines):
        # Strip comments and trailing whitespace to find the bare code portion
        code = lines[idx].split("#")[0].rstrip()
        if code.endswith(":"):
            return idx
        idx += 1
    return def_lineno - 1  # fallback: same line as def


def add_docstring(filepath):
    """Insert the boilerplate docstring into main() methods that lack one.

    Args:
        filepath: Path to the Python file to update

    Returns:
        True if the file was modified, False otherwise
    """
    path = Path(filepath)
    source = path.read_text(encoding="utf-8")
    lines = source.splitlines(keepends=True)

    targets = find_mains_without_docstring(source)
    if not targets:
        return False

    # Process in reverse order so earlier insertions don't shift later line numbers
    for def_lineno, col_offset in sorted(targets, reverse=True):
        sig_end_idx = _find_def_end(lines, def_lineno)
        indent = " " * col_offset
        docstring_line = f'{indent}"""{DOCSTRING}"""\n'
        lines.insert(sig_end_idx + 1, docstring_line)

    path.write_text("".join(lines), encoding="utf-8")
    return True


def main():
    """Execution starts here."""

    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <file.py|directory> [...]")
        sys.exit(1)

    def _iter_py_files(directory):
        for path in sorted(directory.rglob("*.py")):
            if any(
                part.startswith(".") or part in {"site-packages", "venv", "virtualenv"}
                for part in path.parts
            ):
                # print(f"Skipping {path} (hidden or in site-packages)")
                continue
            yield path

    py_files = []
    for arg in sys.argv[1:]:
        target = Path(arg)
        if target.is_dir():
            py_files.extend(_iter_py_files(target))
        elif target.suffix == ".py":
            py_files.append(target)
        else:
            print(f"Skipping non-Python file: {target}")

    changed = 0
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(add_docstring, f): f for f in py_files}
        for future in as_completed(futures):
            f = futures[future]
            try:
                if future.result():
                    print(f"Updated: {f}")
                    changed += 1
            except Exception as exc:
                print(f"Error processing {f}: {exc}")

    print(f"\n{changed} file(s) updated.")


if __name__ == "__main__":
    main()
