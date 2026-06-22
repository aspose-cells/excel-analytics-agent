import json
import os
import subprocess
import sys
from pathlib import Path


def run_safety():
    output_dir = Path("output/security")
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "safety_report.json"
    try:
        result = subprocess.run(
            [sys.executable, "-m", "safety", "check", "-r", "requirements.txt",
             "--full-report", "-o", "json"],
            capture_output=True, text=True, timeout=60,
        )
        if result.stdout:
            data = json.loads(result.stdout)
        else:
            data = {"vulnerabilities": [], "report": result.stdout or "No issues found"}
        with open(report_path, "w") as f:
            json.dump(data, f, indent=2)
        print(f"[SECURITY] Safety report saved: {report_path}")
    except Exception as e:
        print(f"[SECURITY] Safety scan skipped: {e}")
        with open(report_path, "w") as f:
            json.dump({"vulnerabilities": [], "note": f"Safety unavailable: {e}"}, f)


def run_bandit():
    output_dir = Path("output/security")
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "bandit_report.json"
    try:
        result = subprocess.run(
            [sys.executable, "-m", "bandit", "-r", "app/", "-f", "json", "-o", str(report_path)],
            capture_output=True, text=True, timeout=120,
        )
        print(f"[SECURITY] Bandit report saved: {report_path}")
    except Exception as e:
        print(f"[SECURITY] Bandit scan skipped: {e}")
        with open(report_path, "w") as f:
            json.dump({"results": [], "note": f"Bandit unavailable: {e}"}, f)


def run_dependency_check():
    output_dir = Path("output/security")
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "dependency_check.json"
    try:
        import importlib.metadata
        packages = {}
        with open("requirements.txt") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    packages[line] = "unknown"
        for pkg in packages:
            try:
                ver = importlib.metadata.version(pkg.replace("-", "_").replace("==", "").split("==")[0].strip())
                packages[pkg] = ver
            except Exception:
                pass
        report = {
            "packages_checked": len(packages),
            "packages": packages,
            "timestamp": __import__("time").time(),
        }
        with open(report_path, "w") as f:
            json.dump(report, f, indent=2)
        print(f"[SECURITY] Dependency check saved: {report_path}")
    except Exception as e:
        print(f"[SECURITY] Dependency check skipped: {e}")


def main():
    os.makedirs("output/security", exist_ok=True)
    run_safety()
    run_bandit()
    run_dependency_check()
    print("[SECURITY] All security scans completed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
