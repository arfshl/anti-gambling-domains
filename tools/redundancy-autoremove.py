#!/usr/bin/env python3
import argparse
import re
import sys
from pathlib import Path
from typing import List, NamedTuple, Optional, Set


class PurgeResult(NamedTuple):
    removed_count: int
    removed_line_numbers: List[int]
    destination: Path


def extract_redundant_rules(report_path: Path) -> Set[str]:
    """Reads the redundancy report and extracts target rules."""
    if not report_path.is_file():
        raise FileNotFoundError(f"Redundancy report file not found: {report_path}")

    try:
        content = report_path.read_text(encoding="utf-8")
    except Exception as exc:
        raise RuntimeError(f"Failed to read report file '{report_path}': {exc}") from exc

    # Regex matches the rule preceding 'redundant with:'
    pattern = re.compile(r'([^\n]+)\s*\n\s*redundant with:', re.MULTILINE)
    matches = pattern.findall(content)

    return {match.strip() for match in matches if match.strip()}


def purge_redundant_rules(
    input_path: Path,
    target_path: Path,
    output_path: Optional[Path] = None
) -> PurgeResult:
    destination = output_path if output_path else target_path

    if destination.resolve() == input_path.resolve():
        raise ValueError(f"Destination path cannot be equal to input report path: {destination}")

    if not target_path.is_file():
        raise FileNotFoundError(f"Target filter file not found: {target_path}")

    redundant_rules = extract_redundant_rules(input_path)

    try:
        lines = target_path.read_text(encoding="utf-8").splitlines(keepends=True)
    except Exception as exc:
        raise RuntimeError(f"Failed to read target file '{target_path}': {exc}") from exc

    cleaned_lines = []
    removed_line_numbers = []

    # Iterate with index (1-based line numbers)
    for line_num, line in enumerate(lines, start=1):
        if line.strip() in redundant_rules:
            removed_line_numbers.append(line_num)
            continue
        cleaned_lines.append(line)

    try:
        with open(destination, "wb") as f:
            f.write("".join(cleaned_lines).encode("utf-8"))
    except Exception as exc:
        raise RuntimeError(f"Failed to write destination file '{destination}': {exc}") from exc

    return PurgeResult(
        removed_count=len(removed_line_numbers),
        removed_line_numbers=removed_line_numbers,
        destination=destination
    )


def resolve_path(path_str: str) -> Path:
    return Path(path_str).expanduser().resolve()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Auto-purge redundant adblock/DNS rules from a target filter file."
    )
    parser.add_argument(
        "-i", "--input",
        required=True,
        type=str,
        help="Path to the redundancy report file."
    )
    parser.add_argument(
        "-t", "--target",
        required=True,
        type=str,
        help="Path to the target filter list file to be cleaned."
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default=None,
        help="Optional output path. If omitted, the target file will be overwritten."
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    try:
        input_path = resolve_path(args.input)
        target_path = resolve_path(args.target)
        output_path = resolve_path(args.output) if args.output else None

        result = purge_redundant_rules(input_path, target_path, output_path)

        print(f"Removed lines: {result.removed_count}")
        if result.removed_line_numbers:
            line_str = ", ".join(map(str, result.removed_line_numbers))
            print(f"Line numbers: {line_str}")
        else:
            print("Line numbers: None")

    except (FileNotFoundError, ValueError, RuntimeError) as exc:
        print(f"[Error] {exc}", file=sys.stderr)
        sys.exit(1)
    except Exception as exc:
        print(f"[Fatal Error] Unexpected error occurred: {exc}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main()