from pathlib import Path
from typing import List
from dataclasses import dataclass

from rules import Rule
import logging

# Logger for scanner module
logger = logging.getLogger(__name__)


@dataclass
class Finding:
    file: str
    line: int
    match: str
    rule_id: str
    description: str
    severity: str


class Scanner:
    """Scans directories for patterns defined by rules."""

    def __init__(self, rules: List[Rule]):
        self.rules = rules
        logger.debug(f"Initialized Scanner with rules: {rules}")

    def scan_directory(self, path: Path) -> List[Finding]:
        findings: List[Finding] = []
        logger.debug(f"Scanning directory: {path}")
        for file in path.rglob("**/*"):
            if not file.is_file():
                continue
            try:
                if file.stat().st_size > 50 * 1024 * 1024:
                    continue  # skip large files
            except Exception:
                continue
            try:
                text = file.read_text(encoding='utf-8')
            except UnicodeDecodeError:
                try:
                    text = file.read_text(encoding='latin-1')
                except Exception:
                    continue
            for i, line in enumerate(text.splitlines(), start=1):
                for rule in self.rules:
                    for m in rule.regex.finditer(line):
                        findings.append(Finding(
                            file=str(file),
                            line=i,
                            match=m.group(0),
                            rule_id=rule.id,
                            description=rule.description,
                            severity=rule.severity,
                        ))
        logger.info(f"Found {len(findings)} findings in {path}")
        return findings
