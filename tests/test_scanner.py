import tempfile
from pathlib import Path
import pytest
from hermit_shells.scanner import Scanner, Finding
from hermit_shells.rules import Rule

def create_rule(pattern, rule_id="TEST.ID", description="desc", severity="LOW", provider="TEST"):
    return Rule(rule_id, pattern, description, provider, severity)

@ pytest.fixture
def tmp_dir_with_files(tmp_path):
    # Create a small text file with matching and non-matching lines
    dir = tmp_path / "data"
    dir.mkdir()
    file = dir / "test.txt"
    content = "hello world\nmybucket.s3.amazonaws.com/path\nno match here"
    file.write_text(content)
    # Create a large file to test skip (>50MB)
    large_file = dir / "large.txt"
    large_file.write_bytes(b"a" * (51 * 1024 * 1024))
    return dir


def test_scanner_detects_pattern(tmp_dir_with_files):
    rule = create_rule(r"([A-Za-z0-9\-_.]+)\.s3\.amazonaws\.com")
    scanner = Scanner([rule])
    findings = scanner.scan_directory(tmp_dir_with_files)
    assert len(findings) == 1
    f = findings[0]
    assert isinstance(f, Finding)
    assert f.file.endswith("test.txt")
    assert f.line == 2
    assert "mybucket.s3.amazonaws.com" in f.match
    assert f.rule_id == "TEST.ID"


def test_scanner_skips_large_files(tmp_dir_with_files):
    # Rule matches 'a', but file is skipped due to size
    rule = create_rule(r"a")
    scanner = Scanner([rule])
    findings = scanner.scan_directory(tmp_dir_with_files)
    # small file has matches for 'a' in 'hello world' etc, but large file is skipped
    assert any(f.file.endswith("test.txt") for f in findings)
    assert not any(f.file.endswith("large.txt") for f in findings)
