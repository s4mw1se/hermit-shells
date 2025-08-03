import yaml
import tempfile
from pathlib import Path
import pytest

from hermit_shells.rules import load_rules, RuleLoadError

VALID_YAML = '''
- id: "TEST.Rule"
  pattern: "foo.*"
  description: "Test rule"
  cloud_provider: "Test"
  severity: "low"
'''

INVALID_YAML = '''
- id: "TEST.Rule"
  description: "Missing pattern"
'''

def test_load_default_rules(tmp_path):
    # Use a temporary default rules file
    file = tmp_path / "rules.yaml"
    file.write_text(VALID_YAML)
    rules = load_rules(file)
    assert len(rules) == 1
    rule = rules[0]
    assert rule.id == "TEST.Rule"
    assert rule.regex.pattern == "foo.*"
    assert rule.severity == "LOW"

def test_load_external_overrides_default(tmp_path):
    default = tmp_path / "default.yaml"
    default.write_text(VALID_YAML)
    external = tmp_path / "external.yaml"
    external_content = VALID_YAML.replace("TEST.Rule", "EXT.Rule")
    external.write_text(external_content)
    rules = load_rules(default, external)
    assert len(rules) == 1
    assert rules[0].id == "EXT.Rule"

def test_load_invalid_rules(tmp_path):
    file = tmp_path / "bad.yaml"
    file.write_text(INVALID_YAML)
    with pytest.raises(RuleLoadError):
        load_rules(file)
