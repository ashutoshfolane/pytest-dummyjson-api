from __future__ import annotations

import glob
import os
import xml.etree.ElementTree as ET
from dataclasses import dataclass


@dataclass
class Totals:
    files: int = 0
    tests: int = 0
    failures: int = 0
    errors: int = 0
    skipped: int = 0
    time_s: float = 0.0


def _to_int(v: str | None) -> int:
    try:
        return int(v or "0")
    except ValueError:
        return 0


def _to_float(v: str | None) -> float:
    try:
        return float(v or "0")
    except ValueError:
        return 0.0


def parse_junit_files(pattern: str) -> Totals:
    totals = Totals()
    paths = sorted(glob.glob(pattern))
    totals.files = len(paths)

    for p in paths:
        root = ET.parse(p).getroot()

        # Root may be <testsuite> or <testsuites>
        suites = []
        if root.tag == "testsuite":
            suites = [root]
        elif root.tag == "testsuites":
            suites = list(root.findall("testsuite"))
        else:
            # unknown, skip safely
            continue

        for s in suites:
            totals.tests += _to_int(s.attrib.get("tests"))
            totals.failures += _to_int(s.attrib.get("failures"))
            totals.errors += _to_int(s.attrib.get("errors"))
            totals.skipped += _to_int(s.attrib.get("skipped"))
            totals.time_s += _to_float(s.attrib.get("time"))

    return totals


def write_summary_md(md: str) -> None:
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write(md)
    else:
        # local fallback
        print(md)


def main() -> None:
    junit_pattern = os.environ.get("JUNIT_PATTERN", "artifacts/junit-*.xml")
    suite_name = os.environ.get("SUITE_NAME", "Test Run")

    t = parse_junit_files(junit_pattern)

    status = "✅ PASS"
    if t.failures > 0 or t.errors > 0:
        status = "❌ FAIL"

    md = f"""## {suite_name}: {status}

| Metric | Value |
|---|---:|
| JUnit files | {t.files} |
| Tests | {t.tests} |
| Failures | {t.failures} |
| Errors | {t.errors} |
| Skipped | {t.skipped} |
| Time (s) | {t.time_s:.2f} |

**Artifacts**
- HTML report: `artifacts/report-*.html`
- Console log: `artifacts/console-*.log` (sanitized)
- JUnit XML: `artifacts/junit-*.xml`

"""
    write_summary_md(md)


if __name__ == "__main__":
    main()
