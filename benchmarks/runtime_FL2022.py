#!/usr/bin/env python
"""
Baseline/compare-run benchmark for HCV-GAPS (FL-2022 workload).

Example:
    python benchmarks/runtime_FL2022.py --label baseline-v0.9

The script will
1. run the full pipeline (python -m hcv_gaps.main);
2. append a Markdown row to benchmarks/RESULTS.md;
3. save minimal host info to benchmarks/host.json (first run only).
"""
from datetime import datetime
import argparse, subprocess, time, json, platform, pathlib

RESULTS_MD = pathlib.Path("benchmarks/RESULTS.md")
HOST_JSON  = pathlib.Path("benchmarks/host.json")
CMD        = ["python", "-m", "hcv_gaps.main"]     # full pipeline

def main() -> None:
    # ----- CLI arg for the first column label -----
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", default=None,
                    help="Text to appear in the first column of RESULTS.md")
    args = ap.parse_args()
    label = args.label or f"run-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    # ----- Run the pipeline -----
    t0 = time.perf_counter()
    subprocess.run(CMD, check=True)
    seconds = time.perf_counter() - t0
    timestamp = datetime.now().isoformat(timespec="seconds")

    row = f"| {label} | {timestamp} | {seconds:.1f} |"
    print(row)

    # ----- Append to RESULTS.md (create with header if missing) -----
    if not RESULTS_MD.exists():
        RESULTS_MD.write_text("| run label | timestamp | seconds |\n", encoding="utf-8")
    with RESULTS_MD.open("a", encoding="utf-8") as f:
        f.write(row + "\n")

    # ----- Host metadata (first run) -----
    if not HOST_JSON.exists():
        meta = {
            "timestamp": timestamp,
            "python": platform.python_version(),
            "system": platform.platform(),
            "processor": platform.processor(),
        }
        HOST_JSON.write_text(json.dumps(meta, indent=2))

if __name__ == "__main__":
    main()
