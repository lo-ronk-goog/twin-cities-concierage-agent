"""Unit tests for CodeMender CLI orchestrator and integration engine."""

from pathlib import Path
from scripts.codemender import CodeMenderEngine, format_markdown_summary, Finding


def test_codemender_scanner_clean():
    """Verify that CodeMenderEngine confirms app is clean after remediation."""
    root_dir = Path(__file__).resolve().parent.parent.parent
    engine = CodeMenderEngine(root_dir)
    findings = engine.scan_codebase(["app"])
    assert len(findings) == 0


def test_codemender_scanner_detects_vulnerability(tmp_path):
    """Verify that CodeMenderEngine detects unvalidated SQL execution."""
    vuln_file = tmp_path / "unsafe_tool.py"
    vuln_file.write_text("client = bigquery.Client()\nquery_job = client.query(query)\n", encoding="utf-8")
    engine = CodeMenderEngine(tmp_path)
    findings = engine.scan_codebase([tmp_path])
    assert len(findings) == 1
    assert findings[0].severity == "HIGH"
    assert "Unvalidated" in findings[0].title


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


def test_pr_comment_formatting():
    """Verify GitHub PR comment includes 1-click suggestion block."""
    from scripts.codemender import format_pr_comment
    finding = Finding(
        id="TEST-002",
        title="Test Injection",
        severity="HIGH",
        cwe="CWE-89",
        file_path="app/tools.py",
        line_number=20,
        vulnerable_code="client.query(query)",
        remediation_suggestion="Validate query",
        poc_explanation="Exploit description",
        remediated_code="if not query.startswith('SELECT'): raise ValueError()\nclient.query(query)",
    )
    comment = format_pr_comment([finding])
    assert "```suggestion" in comment
    assert "Human-in-the-Loop" in comment
    assert "TEST-002" in comment
