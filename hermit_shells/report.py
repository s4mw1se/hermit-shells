import json
import datetime
from pathlib import Path
from collections import defaultdict
import logging

# Logger for report module
logger = logging.getLogger(__name__)


class ReportGenerator:
    @staticmethod
    def to_json(scanned_directory: Path, findings: list, output_path: Path) -> None:
        logger.debug(
            f"Generating JSON report for directory {scanned_directory} with {len(findings)} findings, writing to {output_path}")
        report = {
            "scanned_directory": str(scanned_directory),
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "findings": [
                {
                    "file": f.file,
                    "line": f.line,
                    "match": f.match,
                    "rule_id": f.rule_id,
                    "description": f.description,
                    "severity": f.severity,
                }
                for f in findings
            ],
        }
        output_path.write_text(json.dumps(report, indent=2))
        logger.info(f"JSON report written to {output_path}")

    @staticmethod
    def to_sarif(scanned_directory: Path, findings: list, output_path: Path) -> None:
        logger.debug(
            f"Generating SARIF report for directory {scanned_directory} with {len(findings)} findings, writing to {output_path}")
        # Map severity to SARIF level
        level_map = {"HIGH": "error", "MEDIUM": "warning", "LOW": "note"}
        # Collect unique rules
        rules_info = {}
        for f in findings:
            if f.rule_id not in rules_info:
                rules_info[f.rule_id] = {
                    "id": f.rule_id,
                    "shortDescription": {"text": f.description},
                    "properties": {"severity": f.severity},
                }
        sarif = {
            "version": "2.1.0",
            "$schema": "https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0-rtm.5.json",
            "runs": [
                {
                    "tool": {
                        "driver": {
                            "name": "cloud_takeover_scanner",
                            "informationUri": "",
                            "rules": list(rules_info.values()),
                        }
                    },
                    "results": [
                        {
                            "ruleId": f.rule_id,
                            "message": {"text": f.description},
                            "locations": [
                                {
                                    "physicalLocation": {
                                        "artifactLocation": {"uri": f.file},
                                        "region": {"startLine": f.line},
                                        "value": f.match,
                                    }
                                }
                            ],
                            "level": level_map.get(f.severity, "warning"),
                        }
                        for f in findings
                    ],
                }
            ],
        }
        output_path.write_text(json.dumps(sarif, indent=2))
        logger.info(f"SARIF report written to {output_path}")
