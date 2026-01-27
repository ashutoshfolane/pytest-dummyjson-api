from __future__ import annotations

import argparse
import json
import os
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# This script produces a stakeholder-friendly metrics snapshot from:
# - JUnit XML (pytest --junitxml=...)
# - Optional flake history JSON (.cache/flakes/history.json)
#
# Outputs:
# - metrics.json (machine readable)
# - metrics.md (human readable)


@dataclass(frozen=True)
class TestCase:
    test_id: str
    classname: str
    name: str
    file: str
    duration_s: float
    outcome: str  # passed|failed|skipped
    failure_message: str | None


def _now_run_id() -> str:
    # Prefer GitHub run id, otherwise epoch seconds.
    return os.getenv("GITHUB_RUN_ID") or str(int(time.time()))


def _safe_float(v: str | None, default: float = 0.0) -> float:
    try:
        return float(v) if v is not None else default
    except Exception:
        return default


def _case_test_id(classname: str, name: str) -> str:
    classname = (classname or "").strip()
    name = (name or "").strip()
    return f"{classname}::{name}" if classname else name


def _extract_file_from_classname(classname: str) -> str:
    # pytest typically sets classname like:
    # - "tests.users.test_users_smoke" or "tests/users/test_users_smoke.py"
    # We'll normalize to something readable.
    c = (classname or "").strip()
    if not c:
        return ""
    if c.endswith(".py"):
        return c
    # dotted module -> module path
    return c.replace(".", "/") + ".py"


def parse_junit(junit_path: Path) -> list[TestCase]:
    """
    Parse JUnit XML and return TestCase entries.
    Outcome rules:
      - failed: <failure> or <error>
      - skipped: <skipped>
      - passed: none of the above
    """
    root = ET.parse(junit_path).getroot()
    cases: list[TestCase] = []

    for tc in root.findall(".//testcase"):
        classname = tc.attrib.get("classname", "") or ""
        name = tc.attrib.get("name", "") or ""
        duration_s = _safe_float(tc.attrib.get("time", "0"))
        test_id = _case_test_id(classname, name)
        file_guess = _extract_file_from_classname(classname)

        failure_node = tc.find("failure") or tc.find("error")
        skipped_node = tc.find("skipped")

        if failure_node is not None:
            outcome = "failed"
            # Keep it short (stakeholder-friendly) but still useful
            msg = (failure_node.attrib.get("message") or "").strip()
            txt = (failure_node.text or "").strip()
            failure_message = msg or (txt.splitlines()[0] if txt else "failed")
        elif skipped_node is not None:
            outcome = "skipped"
            failure_message = None
        else:
            outcome = "passed"
            failure_message = None

        cases.append(
            TestCase(
                test_id=test_id,
                classname=classname,
                name=name,
                file=file_guess,
                duration_s=duration_s,
                outcome=outcome,
                failure_message=failure_message,
            )
        )

    return cases


def load_flake_history(history_path: Path) -> dict[str, list[dict[str, str]]]:
    """
    History format (from flakes.py):
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


def compute_flake_summary(flake_history: dict[str, list[dict[str, str]]]) -> dict[str, Any]:
    """
    A test is a flaky candidate if in its stored window it has
    at least one pass AND at least one fail.
    """
    candidates: list[dict[str, Any]] = []

    for test_id, entries in flake_history.items():
        outcomes = [e.get("outcome") for e in entries]
        passed = outcomes.count("passed")
        failed = outcomes.count("failed")
        skipped = outcomes.count("skipped")

        if passed > 0 and failed > 0:
            candidates.append(
                {
                    "test_id": test_id,
                    "passed": passed,
                    "failed": failed,
                    "skipped": skipped,
                    "total": passed + failed + skipped,
                }
            )

    candidates.sort(key=lambda x: (x["failed"], x["total"]), reverse=True)

    return {
        "history_path": str(flake_history.get("__history_path__", ""))
        if isinstance(flake_history, dict)
        else "",
        "flaky_candidates_count": len(candidates),
        "flaky_candidates": candidates[:20],  # cap for dashboard readability
    }


def build_metrics(
    *,
    suite: str,
    junit_path: Path,
    cases: list[TestCase],
    flake_history: dict[str, list[dict[str, str]]] | None,
) -> dict[str, Any]:
    total = len(cases)
    passed = sum(1 for c in cases if c.outcome == "passed")
    failed = sum(1 for c in cases if c.outcome == "failed")
    skipped = sum(1 for c in cases if c.outcome == "skipped")
    duration_s = sum(c.duration_s for c in cases)

    # Top failing tests (by 1 failure each, but list is still helpful)
    failing_cases = [c for c in cases if c.outcome == "failed"]

    top_failures = []
    for c in failing_cases[:20]:
        top_failures.append(
            {
                "test_id": c.test_id,
                "file": c.file,
                "duration_s": round(c.duration_s, 3),
                "message": c.failure_message or "failed",
            }
        )

    # Slowest tests
    slowest = sorted(cases, key=lambda x: x.duration_s, reverse=True)[:15]
    slowest_tests = [
        {
            "test_id": c.test_id,
            "file": c.file,
            "outcome": c.outcome,
            "duration_s": round(c.duration_s, 3),
        }
        for c in slowest
    ]

    # File-level aggregation (boundary visibility)
    by_file: dict[str, dict[str, Any]] = {}
    for c in cases:
        f = c.file or "(unknown)"
        agg = by_file.setdefault(
            f, {"file": f, "total": 0, "passed": 0, "failed": 0, "skipped": 0, "duration_s": 0.0}
        )
        agg["total"] += 1
        agg[c.outcome] += 1
        agg["duration_s"] += c.duration_s

    files_summary = sorted(by_file.values(), key=lambda x: (x["failed"], x["total"]), reverse=True)
    for item in files_summary:
        item["duration_s"] = round(item["duration_s"], 3)

    # Flake summary
    flake_summary: dict[str, Any] = {"flaky_candidates_count": 0, "flaky_candidates": []}
    if flake_history is not None:
        flake_summary = compute_flake_summary(flake_history)

    # Pass rate (avoid divide by zero)
    pass_rate = (passed / total * 100.0) if total else 0.0

    return {
        "schema_version": 1,
        "run_id": _now_run_id(),
        "suite": suite,
        "junit_path": str(junit_path),
        "summary": {
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "pass_rate_percent": round(pass_rate, 2),
            "duration_s": round(duration_s, 3),
        },
        "top_failures": top_failures,
        "slowest_tests": slowest_tests,
        "files": files_summary[:25],  # cap for readability
        "flakes": flake_summary,
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }


def write_md(out_md: Path, metrics: dict[str, Any]) -> None:
    s = metrics["summary"]
    flakes = metrics.get("flakes", {}) or {}

    lines: list[str] = []
    lines.append(f"# Metrics — {metrics['suite']}\n\n")
    lines.append(f"- Run: `{metrics['run_id']}`\n")
    lines.append(f"- Generated: `{metrics['generated_at_utc']}`\n")
    lines.append(f"- JUnit: `{metrics['junit_path']}`\n\n")

    lines.append("## Summary\n\n")
    lines.append("| Total | Passed | Failed | Skipped | Pass rate | Duration (s) |\n")
    lines.append("|---:|---:|---:|---:|---:|---:|\n")
    lines.append(
        f"| {s['total']} | {s['passed']} | {s['failed']} | {s['skipped']} | {s['pass_rate_percent']}% | {s['duration_s']} |\n\n"
    )

    lines.append("## Flake report (report-only)\n\n")
    lines.append(f"- Flaky candidates: **{flakes.get('flaky_candidates_count', 0)}**\n\n")
    if flakes.get("flaky_candidates"):
        lines.append("| Test | Passed | Failed | Skipped |\n")
        lines.append("|---|---:|---:|---:|\n")
        for c in flakes["flaky_candidates"]:
            lines.append(f"| `{c['test_id']}` | {c['passed']} | {c['failed']} | {c['skipped']} |\n")
        lines.append("\n")

    lines.append("## Top failures\n\n")
    if metrics["top_failures"]:
        lines.append("| Test | File | Duration (s) | Message |\n")
        lines.append("|---|---|---:|---|\n")
        for f in metrics["top_failures"]:
            msg = (f.get("message") or "").replace("\n", " ")
            lines.append(f"| `{f['test_id']}` | `{f['file']}` | {f['duration_s']} | {msg} |\n")
        lines.append("\n")
    else:
        lines.append("✅ No failures.\n\n")

    lines.append("## Slowest tests\n\n")
    lines.append("| Test | Outcome | Duration (s) |\n")
    lines.append("|---|---|---:|\n")
    for t in metrics["slowest_tests"]:
        lines.append(f"| `{t['test_id']}` | {t['outcome']} | {t['duration_s']} |\n")
    lines.append("\n")

    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text("".join(lines), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--suite", required=True, help="Suite name (smoke|regression|contract|...)")
    ap.add_argument(
        "--junit", required=True, help="Path to JUnit XML (e.g. artifacts/junit-smoke.xml)"
    )
    ap.add_argument("--flakes-history", default="", help="Path to flake history JSON (optional)")
    ap.add_argument("--out-json", default="artifacts/metrics.json", help="Output JSON file")
    ap.add_argument("--out-md", default="artifacts/metrics.md", help="Output Markdown file")
    args = ap.parse_args()

    junit_path = Path(args.junit)
    if not junit_path.exists():
        print(f"ERROR: JUnit not found: {junit_path}")
        return 2

    cases = parse_junit(junit_path)

    flake_history: dict[str, list[dict[str, str]]] | None = None
    flakes_history_path = (args.flakes_history or "").strip()
    if flakes_history_path:
        flake_history = load_flake_history(Path(flakes_history_path))

    metrics = build_metrics(
        suite=args.suite,
        junit_path=junit_path,
        cases=cases,
        flake_history=flake_history,
    )

    out_json = Path(args.out_json)
    out_md = Path(args.out_md)

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(metrics, indent=2, sort_keys=True), encoding="utf-8")

    write_md(out_md, metrics)

    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
