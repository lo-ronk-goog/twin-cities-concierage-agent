"""Unit tests for CodeMender CLI orchestrator and integration engine."""

from pathlib import Path
from scripts.codemender import CodeMenderEngine, format_markdown_summary, Finding


def test_codemender_scanner():
    """Verify that CodeMenderEngine scans the workspace and detects findings."""
    root_dir = Path(__file__).resolve().parent.parent.parent
    engine = CodeMenderEngine(root_dir)
    findings = engine.scan_codebase(["app"])
    assert len(findings) > 0
    first = findings[0]
    assert first.severity in ("HIGH", "CRITICAL", "MEDIUM", "LOW")
    assert "SQL" in first.title or "Unvalidated" in first.title
    assert first.file_path.endswith(".py")


def test_markdown_summary_generation():
    """Verify formatting of GitHub Step Summary markdown."""
    finding = Finding(
        id="TEST-001",
        title="Test Vulnerability",
        severity="HIGH",
        cwe="CWE-89",
        file_path="app/test.py",
        line_number=10,
        vulnerable_code="execute(raw)",
        remediation_suggestion="Use parameterization",
        poc_explanation="Exploit payload details",
        remediated_code="execute(safe)",
    )
    md = format_markdown_summary([finding])
    assert "CodeMender Security Gate" in md
    assert "TEST-001" in md
    assert "CWE-89" in md
    assert "Human-in-the-Loop" in md


def test_markdown_summary_clean():
    """Verify passed status when zero findings exist."""
    md = format_markdown_summary([])
    assert "Passed" in md
    assert "No security vulnerabilities" in md
