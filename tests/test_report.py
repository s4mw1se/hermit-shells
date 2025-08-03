import json
from pathlib import Path
import tempfile
from hermit_shells.report import ReportGenerator
from hermit_shells.scanner import Finding

def test_to_json(tmp_path):
    scanned_dir = Path("/tmp/testdir")
    findings = [Finding(file="file1.txt", line=5, match="match", rule_id="RID", description="desc", severity="LOW")]
    out = tmp_path / "report.json"
    ReportGenerator.to_json(scanned_dir, findings, out)
    data = json.loads(out.read_text())
    assert data["scanned_directory"] == str(scanned_dir)
    assert len(data["findings"]) == 1
    assert data["findings"][0]["rule_id"] == "RID"

def test_to_sarif(tmp_path):
    scanned_dir = Path("/tmp/testdir")
    findings = [Finding(file="file1.txt", line=5, match="match", rule_id="RID", description="desc", severity="HIGH")]
    out = tmp_path / "report.sarif"
    ReportGenerator.to_sarif(scanned_dir, findings, out)
    data = json.loads(out.read_text())
    run = data["runs"][0]
    results = run["results"]
    assert results[0]["ruleId"] == "RID"
    assert results[0]["locations"][0]["physicalLocation"]["region"]["startLine"] == 5
