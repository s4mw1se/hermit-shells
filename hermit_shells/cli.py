import sys
from pathlib import Path
import logging
import json
import yaml
import typer
from rules import load_rules
from scanner import Scanner
from report import ReportGenerator
# removed unused Rule import


def configure_logging(verbose: bool):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level, format="%(asctime)s [%(levelname)s] %(message)s")


app = typer.Typer(help="Cloud Resource Takeover Scanner CLI")


@app.command()
def scan(
    cache_dir: Path = typer.Option(..., "--cache-dir",
                                   exists=True, file_okay=False, help="Directory to scan"),
    config: Path = typer.Option(
        None, "--config", exists=True, file_okay=True, help="External YAML rules file"),
    json_out: Path = typer.Option(
        None, "--json-out", help="Path to JSON output file"),
    sarif_out: Path = typer.Option(
        None, "--sarif-out", help="Path to SARIF output file"),
    fail_on: str = typer.Option(None, "--fail-on", case_sensitive=False,
                                help="Fail on severity level (HIGH, MEDIUM, LOW)"),
    verbose: bool = typer.Option(
        False, "--verbose", "-v", help="Enable verbose logging")
) -> None:
    """Scan a directory for cloud resource takeover patterns."""
    configure_logging(verbose)
    logger = logging.getLogger(__name__)
    # Debug logging configuration details
    logger.debug(f"Logging configured. verbose={verbose}")

    logger.info(
        f"Loading rules (default + {'external' if config else 'no extra'} config)")
    default_rules_path = Path(__file__).parent / "rules_default.yaml"
    rules = load_rules(default_rules_path, config)
    logger.debug(f"Loaded {len(rules)} rules from configuration")

    logger.info(f"Scanning directory: {cache_dir}")
    scanner = Scanner(rules)
    logger.debug(f"Initialized Scanner with rule IDs: {[r.id for r in rules]}")
    findings = scanner.scan_directory(cache_dir)
    for f in findings:
        logger.debug(
            f"Finding: {f.file}:{f.line} - {f.match} (Rule: {f.rule_id}, Severity: {f.severity})")
    if not findings:
        logger.info("No potential issues found")
    else:
        logger.info(f"Found {len(findings)} potential issues")

    # Generate JSON output
    if json_out:
        logger.info(f"Writing JSON report to {json_out}")
        ReportGenerator.to_json(cache_dir, findings, json_out)

    # Generate SARIF output
    if sarif_out:
        logger.info(f"Writing SARIF report to {sarif_out}")
        ReportGenerator.to_sarif(cache_dir, findings, sarif_out)

    # Determine exit code based on severity
    levels = [f.severity.upper() for f in findings]
    severity_rank = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
    highest = max((severity_rank.get(l, 0) for l in levels), default=0)
    exit_code = 0
    if fail_on and highest >= severity_rank.get(fail_on.upper(), 0):
        exit_code = 1
    sys.exit(exit_code)


if __name__ == "__main__":
    app()
