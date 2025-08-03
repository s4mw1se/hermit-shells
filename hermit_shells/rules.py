import yaml
import re
from pathlib import Path
from typing import List, Optional
import logging

# Logger for rules module
logger = logging.getLogger(__name__)


class Rule:
    """Represents a scanning rule loaded from YAML."""

    def __init__(self, id: str, pattern: str, description: str, cloud_provider: str, severity: str):
        self.id = id
        self.pattern = pattern
        self.description = description
        self.cloud_provider = cloud_provider
        self.severity = severity.upper()
        self.regex = re.compile(pattern)


class RuleLoadError(Exception):
    pass


def load_rules(default_path: Path, external_path: Optional[Path] = None) -> List[Rule]:
    """Load rules from default YAML and optionally override with external YAML."""
    logger.debug(f"Loading default rules from {default_path}")
    # Load default rules
    try:
        default_data = yaml.safe_load(default_path.read_text()) or []
    except Exception as e:
        raise RuleLoadError(f"Failed to load default rules: {e}")
    logger.debug(f"Loaded {len(default_data)} default rules")

    rules_data = default_data
    # Override with external if provided
    if external_path:
        logger.debug(f"Loading external rules from {external_path}")
        try:
            external_data = yaml.safe_load(external_path.read_text()) or []
            rules_data = external_data
        except Exception as e:
            raise RuleLoadError(f"Failed to load external rules: {e}")
        logger.debug(f"Loaded {len(external_data)} external rules")

    rules: List[Rule] = []
    for idx, r in enumerate(rules_data):
        try:
            rid = r["id"]
            pattern = r["pattern"]
            desc = r.get("description", "")
            provider = r.get("cloud_provider", "")
            severity = r.get("severity", "LOW")
        except KeyError as e:
            raise RuleLoadError(
                f"Missing required rule field {e} in rule index {idx}")
        try:
            rule = Rule(rid, pattern, desc, provider, severity)
        except re.error as e:
            raise RuleLoadError(f"Invalid regex in rule {rid}: {e}")
        rules.append(rule)
    logger.debug(f"Returning total {len(rules)} rules")
    return rules
