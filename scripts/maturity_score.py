import os
import ast
import json
import glob
import re
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def count_python_files(paths):
    files = []
    for p in paths:
        full = PROJECT_ROOT / p
        if full.is_dir():
            files.extend(glob.glob(str(full / "**/*.py"), recursive=True))
        elif full.is_file():
            files.append(str(full))
    return [f for f in files if "venv" not in f and "__pycache__" not in f]


def extract_functions_and_classes(filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return [], []
    functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
    classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    return functions, classes


def has_type_hints(functions):
    hinted = 0
    for fn in functions:
        has_returns = fn.returns is not None
        has_args = any(
            a.annotation is not None
            for a in fn.args.args
            if a.arg != "self"
        )
        if has_returns or has_args:
            hinted += 1
    return hinted, len(functions)


def has_docstrings(functions, classes):
    doc_count = 0
    total = len(functions) + len(classes)
    for fn in functions:
        if ast.get_docstring(fn):
            doc_count += 1
    for cls in classes:
        if ast.get_docstring(cls):
            doc_count += 1
    return doc_count, total


def has_logging(filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    return bool(re.search(r"(import logging|from logging|logging\.|logger\.|from app\.logger)", content))


def has_error_handling(filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        content = f.read()
    return bool(re.search(r"(try:|except|raise\s|Exception|ExcelAgentError|AnalysisError|PipelineError|PlannerError|ExcelReadError|ExcelWriteError|ToolNotFoundError|ConfigurationError|StateError)", content))


def count_lines(filepath):
    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        return len(f.readlines())


class MaturityScorer:
    def __init__(self, project_root=PROJECT_ROOT):
        self.root = Path(project_root)
        self.report = {}

    def collect_metrics(self):
        self.source_files = count_python_files(["app", "tests", "scripts", "config.py", "main.py"])
        self.test_files = [f for f in self.source_files if "/test_" in f or "\\test_" in f]
        self.app_files = [f for f in self.source_files if f.startswith(str(self.root / "app"))]

        self.total_functions = 0
        self.total_classes = 0
        self.hinted_functions = 0
        self.docstring_items = 0
        self.files_with_logging = 0
        self.files_with_error_handling = 0
        self.total_lines = 0

        self.has_examples = (self.root / "samples").is_dir()
        self.has_docker = (self.root / "docker" / "Dockerfile").is_file()
        self.has_compose = (self.root / "docker" / "docker-compose.yml").is_file()
        self.has_readme = any(self.root.glob("README*"))
        self.has_ci = (self.root / ".gitlab-ci.yml").is_file()
        self.has_gitignore = (self.root / ".gitignore").is_file()
        self.has_git = (self.root / ".git").is_dir()
        self.has_config = (self.root / "config.py").is_file()
        self.has_dotenv = (self.root / ".env").is_file() or (self.root / ".env.example").is_file()
        self.has_requirements = (self.root / "requirements.txt").is_file()
        self.has_pyproject = (self.root / "pyproject.toml").is_file()
        self.has_docs = bool(list(self.root.glob("docs/*"))) or self.has_readme
        self.has_main = (self.root / "main.py").is_file()
        self.has_changelog = (self.root / "CHANGELOG.md").is_file()
        self.has_contributing = (self.root / "CONTRIBUTING.md").is_file()
        self.has_codeowners = (self.root / "CODEOWNERS").is_file() or (self.root / ".github" / "CODEOWNERS").is_file()
        self.has_license = (self.root / "LICENSE").is_file() or (self.root / "LICENSE.txt").is_file()
        self.has_security = (self.root / "SECURITY.md").is_file()
        self.has_logger_module = (self.root / "app" / "logger.py").is_file()
        self.has_exceptions_module = (self.root / "app" / "exceptions.py").is_file()
        self.has_state_module = (self.root / "app" / "state.py").is_file()
        self.has_health_module = (self.root / "app" / "health.py").is_file()
        self.has_learning_module = (self.root / "app" / "learning.py").is_file()
        self.has_resilience_module = (self.root / "app" / "resilience.py").is_file()
        self.has_scheduler_module = (self.root / "app" / "scheduler.py").is_file()
        self.has_benchmarks = (self.root / "tests" / "benchmarks" / "test_performance.py").is_file()
        self.has_security_script = (self.root / "scripts" / "security_scan.py").is_file()
        self.has_compliance_docs = (self.root / "docs" / "compliance" / "README.md").is_file()
        self.has_verification_docs = (self.root / "docs" / "verification" / "README.md").is_file()
        self.has_assurance_docs = (self.root / "docs" / "assurance" / "README.md").is_file()

        for fp in self.app_files:
            fn, cls = extract_functions_and_classes(fp)
            self.total_functions += len(fn)
            self.total_classes += len(cls)
            h, _ = has_type_hints(fn)
            self.hinted_functions += h
            d, _ = has_docstrings(fn, cls)
            self.docstring_items += d
            if has_logging(fp):
                self.files_with_logging += 1
            if has_error_handling(fp):
                self.files_with_error_handling += 1
            self.total_lines += count_lines(fp)

        self.tool_registry_exists = (self.root / "app" / "registry" / "tool_registry.py").is_file()
        self.pipeline_files = len(list((self.root / "app" / "pipeline").glob("*.py")))
        self.analysis_files = len(list((self.root / "app" / "analysis").glob("*.py")))
        self.tool_files = len(list((self.root / "app" / "tools").glob("*.py")))

    # ================================================================
    # S — Agent Score
    # ================================================================
    def score_agent(self):
        hinted_pct = (self.hinted_functions / max(self.total_functions, 1)) * 100
        doc_pct = (self.docstring_items / max(self.total_functions + self.total_classes, 1)) * 100

        checks = {
            "features_completeness": min(100, self.analysis_files * 6 + self.tool_files * 6),
            "has_tests": 100 if len(self.test_files) >= 10 else (len(self.test_files) * 10),
            "has_ci_cd": 100 if self.has_ci else 0,
            "has_docker": 100 if self.has_docker else 0,
            "has_documentation": 100 if self.has_docs and self.has_readme else 50,
            "type_hints": min(100, int(hinted_pct)),
            "docstrings": min(100, int(doc_pct)),
            "error_handling": min(100, int(self.files_with_error_handling / max(len(self.app_files), 1) * 100)),
            "logging": min(100, int(self.files_with_logging / max(len(self.app_files), 1) * 100)),
            "config_management": 100 if self.has_config and self.has_dotenv else 50,
            "code_modularity": 100 if len(self.app_files) >= 15 else (len(self.app_files) * 5),
            "dependency_management": 100 if self.has_requirements and self.has_pyproject else 50,
            "has_examples": 100 if self.has_examples else 0,
            "has_license": 100 if self.has_license else 0,
            "has_security_policy": 100 if self.has_security else 0,
        }
        raw = sum(checks.values()) / len(checks)
        level = int(raw // 10)
        return {
            "score": raw,
            "level": f"S{min(9, level)}",
            "label": self._s_label(raw),
            "checks": checks,
        }

    @staticmethod
    def _s_label(raw):
        if raw < 10: return "Minimal Readiness"
        if raw < 20: return "Early Signals"
        if raw < 30: return "Emerging Structure"
        if raw < 40: return "Functional Baseline"
        if raw < 50: return "Usable Readiness"
        if raw < 60: return "Operational Baseline"
        if raw < 70: return "Strong Readiness"
        if raw < 80: return "Advanced Readiness"
        if raw < 90: return "Strategic Readiness"
        return "Exceptional Readiness"

    # ================================================================
    # A — Agentic
    # ================================================================
    def score_agentic(self):
        checks = {
            "has_automation": 20 if self.has_main else 0,
            "llm_integration": 100 if self._has_llm_lib() else 0,
            "multi_step_pipeline": min(80, self.pipeline_files * 25),
            "state_persistence": 100 if self.has_state_module else 0,
            "error_framework": 100 if self.has_exceptions_module else 0,
            "validation_gates": 100 if self.has_ci else 0,
            "tool_registry": 100 if self.tool_registry_exists else 0,
            "dynamic_discovery": 100 if self.tool_registry_exists else 0,
            "health_monitoring": 100 if self.has_health_module else 0,
            "autonomous_execution": 90 if self.has_main and self.has_scheduler_module and self._has_llm_lib() else 60 if self.has_main and self._has_llm_lib() else 0,
            "self_improvement": 100 if self.has_learning_module else 0,
        }
        raw = sum(checks.values()) / len(checks)
        level = int(raw // 10)
        return {
            "score": raw,
            "level": f"A{min(9, level)}",
            "label": self._a_label(raw),
            "checks": checks,
        }

    @staticmethod
    def _a_label(raw):
        if raw < 10: return "None"
        if raw < 20: return "Deterministic"
        if raw < 30: return "Reactive"
        if raw < 40: return "Workflow"
        if raw < 50: return "Stateful"
        if raw < 60: return "Controlled"
        if raw < 70: return "Coordinated"
        if raw < 80: return "Adaptive"
        if raw < 90: return "Autonomous"
        return "Self-Improving"

    # ================================================================
    # P — Practices
    # ================================================================
    def score_practices(self):
        checks = {
            "project_structure": 50 if len(self.app_files) >= 5 else 20,
            "test_coverage": min(100, len(self.test_files) * 8),
            "dependency_management": 100 if self.has_requirements and self.has_pyproject else 50,
            "ci_pipeline": 100 if self.has_ci else 0,
            "docker_build": 100 if self.has_docker else 0,
            "logging_infra": 100 if self.has_logger_module else 0,
            "health_checks": 100 if self.has_health_module else 0,
            "type_hints_pct": min(100, int((self.hinted_functions / max(self.total_functions, 1)) * 100)),
            "docstrings_pct": min(100, int((self.docstring_items / max(self.total_functions + self.total_classes, 1)) * 100)),
            "error_framework": 100 if self.has_exceptions_module else 0,
            "error_handling_pct": min(100, int(self.files_with_error_handling / max(len(self.app_files), 1) * 100)),
            "logging_pct": min(100, int(self.files_with_logging / max(len(self.app_files), 1) * 100)),
            "security_scanning": 100 if self.has_security_script else 0,
            "self_healing": 100 if self.has_resilience_module else 0,
        }
        raw = sum(checks.values()) / len(checks)
        level = int(raw // 10)
        return {
            "score": raw,
            "level": f"P{min(9, level)}",
            "label": self._p_label(raw),
            "checks": checks,
        }

    @staticmethod
    def _p_label(raw):
        if raw < 10: return "None"
        if raw < 20: return "Sparse"
        if raw < 30: return "Structured"
        if raw < 40: return "Gated"
        if raw < 50: return "Automated"
        if raw < 60: return "Observable"
        if raw < 70: return "Verified"
        if raw < 80: return "Resilient"
        if raw < 90: return "Proactive"
        return "Self-Sustaining"

    # ================================================================
    # R — Readiness
    # ================================================================
    def score_readiness(self):
        checks = {
            "docker_deployable": 100 if self.has_docker else 0,
            "code_ownership": 100 if self.has_codeowners else 0,
            "contributing_guide": 100 if self.has_contributing else 0,
            "changelog": 100 if self.has_changelog else 0,
            "version_control": 100 if self.has_git else 0,
            "license": 100 if self.has_license else 0,
            "security_policy": 100 if self.has_security else 0,
            "state_persistence": 100 if self.has_state_module else 0,
            "logging_infra": 100 if self.has_logger_module else 0,
            "ci_cd_pipeline": 100 if self.has_ci else 0,
            "env_config": 100 if self.has_dotenv and self.has_config else 50,
            "compliance_framework": 100 if self.has_compliance_docs else 0,
            "independent_verification": 95 if self.has_verification_docs else 0,
            "formal_assurance": 90 if self.has_assurance_docs else 0,
        }
        raw = sum(checks.values()) / len(checks)
        level = int(raw // 10)
        return {
            "score": raw,
            "level": f"R{min(9, level)}",
            "label": self._r_label(raw),
            "checks": checks,
        }

    @staticmethod
    def _r_label(raw):
        if raw < 10: return "None"
        if raw < 20: return "Deployed"
        if raw < 30: return "Owned"
        if raw < 40: return "Released"
        if raw < 50: return "Governed"
        if raw < 60: return "Auditable"
        if raw < 70: return "Controlled"
        if raw < 80: return "Compliant"
        if raw < 90: return "Verified"
        return "Assured"

    # ================================================================
    # V — Evidence Coverage
    # ================================================================
    def score_evidence(self):
        test_source_ratio = min(100, int(len(self.test_files) / max(len(self.app_files), 1) * 100))
        validation_scripts = len(list((self.root / "scripts").glob("*.py")))

        checks = {
            "has_unit_tests": min(100, len(self.test_files) * 8),
            "has_integration_tests": 100 if any("flow" in f or "full" in f for f in self.test_files) else 50,
            "test_to_source_ratio": test_source_ratio,
            "ci_test_execution": 100 if self.has_ci else 0,
            "validation_scripts": min(100, validation_scripts * 25),
            "code_ownership_docs": 100 if self.has_codeowners else 0,
            "contributing_guide": 100 if self.has_contributing else 0,
            "performance_benchmarks": 100 if self.has_benchmarks else 0,
            "security_scanning_evidence": 100 if self.has_security_script else 0,
            "coverage_tracking": 100 if self.has_ci else 0,
        }
        raw = sum(checks.values()) / len(checks)
        level = int(raw // 10)
        return {
            "score": raw,
            "level": f"V{min(9, level)}",
            "label": self._v_label(raw),
            "checks": checks,
        }

    @staticmethod
    def _v_label(raw):
        if raw < 10: return "Claim-Only"
        if raw < 20: return "Sparse"
        if raw < 30: return "Sampled"
        if raw < 40: return "Partial"
        if raw < 50: return "Sufficient"
        if raw < 60: return "Broad"
        if raw < 70: return "Strong"
        if raw < 80: return "Deep"
        if raw < 90: return "Traceable"
        return "Audit-Grade"

    def _has_llm_lib(self):
        if not self.has_requirements:
            return False
        try:
            return bool(re.search(r"openai", open(self.root / "requirements.txt", encoding="utf-8").read()))
        except Exception:
            return False

    def run(self):
        self.collect_metrics()
        self.report = {
            "project": self.root.name,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
            "metrics": {
                "source_files": len(self.source_files),
                "app_files": len(self.app_files),
                "test_files": len(self.test_files),
                "total_lines": self.total_lines,
                "total_functions": self.total_functions,
                "total_classes": self.total_classes,
                "hinted_functions": self.hinted_functions,
                "docstring_items": self.docstring_items,
                "files_with_logging": self.files_with_logging,
                "files_with_error_handling": self.files_with_error_handling,
            },
            "agent_score": self.score_agent(),
            "agentic": self.score_agentic(),
            "practices": self.score_practices(),
            "readiness": self.score_readiness(),
            "evidence": self.score_evidence(),
        }
        return self.report

    def print_summary(self):
        dims = [
            ("agent_score", "Agent Score"),
            ("agentic", "Agentic"),
            ("practices", "Practices"),
            ("readiness", "Readiness"),
            ("evidence", "Evidence"),
        ]
        print("=" * 70)
        print(f"  Project: {self.report['project']}")
        print(f"  Scored at: {self.report['timestamp']}")
        print("=" * 70)
        print()
        print(f"  {'Dimension':<20} {'Score':<10} {'Level':<8}  {'Label'}")
        print(f"  {'-'*20} {'-'*10} {'-'*8}  {'-'*30}")
        for key, label in dims:
            d = self.report[key]
            print(f"  {label:<20} {d['score']:<10.1f} {d['level']:<8}  {d['label']}")
        print()
        print("  Metrics Summary:")
        m = self.report["metrics"]
        print(f"    Source: {m['source_files']}  App: {m['app_files']}  Tests: {m['test_files']}  Lines: {m['total_lines']}")
        print(f"    Functions: {m['total_functions']}  Classes: {m['total_classes']}")
        print(f"    Type-hinted: {m['hinted_functions']}  Docstrings: {m['docstring_items']}")
        print(f"    Logging: {m['files_with_logging']}/{m['app_files']}  Error handling: {m['files_with_error_handling']}/{m['app_files']}")
        print("=" * 70)


def main():
    scorer = MaturityScorer()
    report = scorer.run()
    scorer.print_summary()

    output_path = PROJECT_ROOT / "output" / "maturity_score.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nFull report saved to: {output_path}")

    return 0 if report["agent_score"]["score"] >= 30 else 1


if __name__ == "__main__":
    sys.exit(main())
