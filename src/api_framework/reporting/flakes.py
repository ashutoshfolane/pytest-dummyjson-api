from __future__ import annotations

import argparse
import json
import os
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Literal

Outcome = Literal["passed", "failed", "skipped"]


@dataclass(frozen=True)
class CaseResult:
    test_id: str  # stable identifier: "classname::name"
    outcome: Outcome


def _now_run_id() -> str:
    # Prefer GitHub run id, otherwise epoch seconds.
    return os.getenv("GITHUB_RUN_ID") or str(int(time.time()))


def _case_test_id(classname: str, name: str) -> str:
    classname = (classname or "").strip()
    name = (name or "").strip()
    return f"{classname}::{name}" if classname else name


def parse_junit(junit_path: Path) -> list[CaseResult]:
    """
    Parse JUnit XML and return outcome per testcase.
    - failed: <failure> or <error>
    - skipped: <skipped>
    - passed: none of the above
    """
    root = ET.parse(junit_path).getroot()
    results: list[CaseResult] = []

    for tc in root.findall(".//testcase"):
        classname = tc.attrib.get("classname", "")
        name = tc.attrib.get("name", "")
        test_id = _case_test_id(classname, name)

        if tc.find("failure") is not None or tc.find("error") is not None:
            outcome: Outcome = "failed"
        elif tc.find("skipped") is not None:
            outcome = "skipped"
        else:
            outcome = "passed"

        results.append(CaseResult(test_id=test_id, outcome=outcome))

    return results


def load_history(history_path: Path) -> dict[str, list[dict[str, str]]]:
    """
    History format:
    {
      "classname::test_name": [{"run_id":"123","outcome":"passed"}, ...]
    }
    """
    if not history_path.exists():
        return {}
    try:
        return json.loads(history_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def save_history(history_path: Path, history: dict[str, list[dict[str, str]]]) -> None:
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text(json.dumps(history, indent=2, sort_keys=True), encoding="utf-8")


def update_history(
    history: dict[str, list[dict[str, str]]],
    results: list[CaseResult],
    *,
    run_id: str,
    window: int,
) -> dict[str, list[dict[str, str]]]:
    # Index latest outcome per test (if duplicate entries exist, last wins)
    latest: dict[str, Outcome] = {}
    for r in results:
        latest[r.test_id] = r.outcome

    for test_id, outcome in latest.items():
        history.setdefault(test_id, [])
        history[test_id].append({"run_id": run_id, "outcome": outcome})

        # Keep last N entries only
        if len(history[test_id]) > window:
            history[test_id] = history[test_id][-window:]

    return history


def compute_flaky_candidates(
    history: dict[str, list[dict[str, str]]],
) -> list[tuple[str, dict[str, int]]]:
    """
    A test is "flaky candidate" if within the stored window it has
    at least one pass AND at least one fail.
    """
    candidates: list[tuple[str, dict[str, int]]] = []

    for test_id, entries in history.items():
        outcomes = [e.get("outcome") for e in entries]
        passed = outcomes.count("passed")
        failed = outcomes.count("failed")
        skipped = outcomes.count("skipped")

        if passed > 0 and failed > 0:
            candidates.append((test_id, {"passed": passed, "failed": failed, "skipped": skipped}))

    # Most suspicious first: more failures, then more total activity
    candidates.sort(
        key=lambda x: (x[1]["failed"], x[1]["passed"] + x[1]["failed"] + x[1]["skipped"]),
        reverse=True,
    )
    return candidates


def write_report_md(
    out_md: Path,
    *,
    junit_path: Path,
    history_path: Path,
    run_id: str,
    window: int,
    candidates: list[tuple[str, dict[str, int]]],
) -> None:
    lines: list[str] = []
    lines.append("# Flake report (small-history)\n\n")
    lines.append(f"- Run: `{run_id}`\n")
    lines.append(f"- JUnit: `{junit_path}`\n")
    lines.append(f"- History: `{history_path}` (window={window})\n")
    lines.append(
        "- Definition: a test is a **flaky candidate** if it has both **PASS** and **FAIL** within the history window\n"
    )
    lines.append(f"- Flaky candidates: **{len(candidates)}**\n\n")

    if not candidates:
        lines.append("✅ No flaky candidates detected in the current history window.\n")
    else:
        lines.append("## Flaky candidates\n\n")
        lines.append("| Test | Passed | Failed | Skipped |\n")
        lines.append("|---|---:|---:|---:|\n")
        for test_id, stats in candidates:
            lines.append(
                f"| `{test_id}` | {stats['passed']} | {stats['failed']} | {stats['skipped']} |\n"
            )

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--junit", required=True, help="Path to JUnit XML (e.g. artifacts/junit-smoke.xml)"
    )
    ap.add_argument("--history", default=".cache/flakes/history.json", help="History JSON path")
    ap.add_argument("--window", type=int, default=20, help="How many recent runs to keep per test")
    ap.add_argument("--out-md", default="artifacts/flake-report.md", help="Output markdown report")
    args = ap.parse_args()

    junit_path = Path(args.junit)
    history_path = Path(args.history)
    out_md = Path(args.out_md)

    if not junit_path.exists():
        print(f"ERROR: JUnit not found: {junit_path}")
        return 2

    run_id = _now_run_id()

    results = parse_junit(junit_path)
    history = load_history(history_path)
    history = update_history(history, results, run_id=run_id, window=args.window)
    save_history(history_path, history)

    candidates = compute_flaky_candidates(history)
    write_report_md(
        out_md,
        junit_path=junit_path,
        history_path=history_path,
        run_id=run_id,
        window=args.window,
        candidates=candidates,
    )

    print(f"Wrote {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
