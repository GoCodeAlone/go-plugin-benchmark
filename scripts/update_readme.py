#!/usr/bin/env python3
"""Parse `go test -bench` output and update the benchmark table in README.md."""

import re
import sys
from pathlib import Path

# Maps the b.Run sub-benchmark name → regex that uniquely identifies the
# corresponding row in the README Markdown table.
BENCH_TO_ROW_PATTERN: dict[str, str] = {
    "golang-plugin":        r"golang\.org/pkg/plugin",
    "hashicorp-go-plugin":  r"github\.com/hashicorp/go-plugin",
    "gocodalone-go-plugin": r"github\.com/GoCodeAlone/go-plugin",
    "pie":                  r"github\.com/natefinch/pie",
    "pingo-tcp":            r"github\.com/dullgiulio/pingo.*\btcp\b",
    "pingo-unix":           r"github\.com/dullgiulio/pingo.*\bunix\b",
    "plug":                 r"github\.com/elliotmr/plug",
    "yaegi":                r"github\.com/traefik/yaegi",
    "gocodalone-yaegi":     r"github\.com/GoCodeAlone/yaegi",
    "wazero":               r"github\.com/tetratelabs/wazero",
}

# Matches: BenchmarkFoo/sub-name-8    12345    67.89 ns/op
# Non-greedy (\S+?) correctly handles names like "hashicorp-go-plugin-8"
# by expanding until the trailing -<digits> is consumed.
_BENCH_LINE_RE = re.compile(
    r"^Benchmark\w+/(\S+?)-\d+\s+(\d+)\s+([\d.]+)\s+ns/op"
)

# Matches the ops and ns/op cells in a Markdown table row, e.g.:
#   |           44219324            |             30.35 ns/op |
# or the TBD placeholders:
#   |             TBD               |                     TBD |
_CELL_RE = re.compile(
    r"\|\s*(?:\d+|TBD)\s*\|\s*(?:[\d.]+ ns/op|TBD)\s*\|"
)

# Column widths used when writing updated values back into the table.
_OPS_WIDTH = 13
_NS_WIDTH = 11

def parse_bench_output(text: str) -> dict[str, tuple[int, str]]:
    """Return {sub_benchmark_name: (ops, ns_per_op_str)} for each result."""
    results: dict[str, tuple[int, str]] = {}
    for line in text.splitlines():
        m = _BENCH_LINE_RE.match(line)
        if m:
            sub_name, ops_str, ns_str = m.group(1), m.group(2), m.group(3)
            results[sub_name] = (int(ops_str), ns_str)
    return results


def update_readme(readme_path: Path, results: dict[str, tuple[int, str]]) -> int:
    """Update the benchmark table in the README in-place.

    Returns the number of rows updated.
    """
    text = readme_path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    updated_count = 0

    for sub_name, (ops, ns) in results.items():
        pattern_str = BENCH_TO_ROW_PATTERN.get(sub_name)
        if not pattern_str:
            print(
                f"  warning: no README row pattern for benchmark '{sub_name}'",
                file=sys.stderr,
            )
            continue

        row_pattern = re.compile(pattern_str)
        for i, line in enumerate(lines):
            if not line.startswith("|"):  # only update Markdown table rows
                continue
            if not row_pattern.search(line):
                continue
            replacement = f"| {ops:>{_OPS_WIDTH}} | {ns:>{_NS_WIDTH}} ns/op |"
            new_line = _CELL_RE.sub(replacement, line.rstrip("\n")) + "\n"
            if new_line != line:
                lines[i] = new_line
                updated_count += 1
            break

    readme_path.write_text("".join(lines), encoding="utf-8")
    return updated_count


def main() -> None:
    bench_output = sys.stdin.read()
    results = parse_bench_output(bench_output)

    if not results:
        print(
            "No benchmark results found in input — README not modified.",
            file=sys.stderr,
        )
        sys.exit(1)

    readme_path = Path(__file__).resolve().parent.parent / "README.md"
    updated = update_readme(readme_path, results)

    print(f"Updated {updated} row(s) in {readme_path.name}.")
    for name, (ops, ns) in sorted(results.items()):
        print(f"  {name:30s}  {ops:>12,} ops   {ns:>8} ns/op")


if __name__ == "__main__":
    main()
