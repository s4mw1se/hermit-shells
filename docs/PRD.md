# Cloud Resource Takeover Scanner CLI – Project Documentation

## Product Requirements Document (v1.0.0)

### Vision and Background

Recent supply-chain attacks have shown that abandoned cloud resources such as
S3 buckets or Azure storage endpoints can be hijacked to serve malicious
content without altering package sources.  This scanner aims to provide
automated visibility into such takeover risks by statically searching build or
dependency caches for references to cloud resources that could be claimed by
attackers.

### Target Users and Use Case

DevSecOps engineers integrate the tool into CI pipelines.  After dependencies
are installed, the scanner runs over cache directories without user
interaction, producing a report of risky URLs and line numbers.

### Key Features

* **Configurable scan directory** – recursively scan any directory for cloud
  references.
* **Pattern detection** – regex rules identify candidate resources across AWS
  S3/CloudFront, Azure Blob/CDN, GCP Storage, and similar services.
* **Severity classification** – findings are labelled High/Medium/Low based on
  rule-driven likelihood of takeover.
* **Output formats** – machine readable JSON and SARIF 2.1.0 reports, with
  non‑zero exit on configurable severity.
* **Non‑interactive CLI** – configuration via arguments or environment
  variables only.
* **Extensibility** – optional external YAML rules file allows custom patterns
  and severity levels.
* **Performance** – multithreaded scanning and compiled regexes provide fast
  analysis without network calls.

### Constraints and Assumptions

The scanner operates offline, treats files as text, skips un-decodable data,
and performs no modification of scanned files.  False positives are preferred
over misses and rule accuracy may evolve over time.

### Success Criteria

Version 1.0.0 is considered successful when it runs easily in CI, detects known
test cases for AWS/Azure/GCP, produces valid JSON and SARIF outputs, and scans
typical dependency caches in minutes without crashes.

## Architectural Design Requirements

### Overview

The project is a modular Python 3.11+ CLI composed of a CLI interface, a core
scanning engine, rules management, and report generators.  Source code follows
the `src/` layout and leverages modern Python features such as type hints,
dataclasses, and enumerations.

### Library Choices

* **CLI** – Typer for argument parsing and auto‑generated help.
* **YAML** – PyYAML with `safe_load` for secure rule parsing.
* **Regex** – pre‑compiled patterns using Python's `re` (or optional `re2`).
* **Reporting** – built‑in `json` for JSON and a SARIF helper library for
  standards‑compliant output.
* **Logging** – Python `logging` with optional verbosity flag.

### Rules Management

Rules live in a YAML file (`rules_default.yaml`) packaged with the tool.
Users may supply their own YAML config to extend or override defaults. Each
rule includes an ID, regex pattern, description, cloud provider, and severity.

### Scanning Logic

The scanner walks files in the target directory, reading line‑by‑line with
graceful decoding fallback.  For every line, each compiled rule is evaluated;
matches produce findings noting file path, line number, snippet, rule ID, and
severity.  Optional thread pools parallelize file scanning.

### Output Generation

After scanning, findings are serialized to JSON and/or SARIF.  SARIF output
maps severities to standard levels (High→error, Medium→warning, Low→note) and
includes rule metadata and result locations.  A configurable severity threshold
can cause the CLI to exit with a non‑zero code.

### Configuration and Extensibility

The architecture anticipates future providers and rule sets; adding new rules
requires only YAML updates.  Code is documented, follows PEP 8, and is covered
by unit tests residing in `tests/`.

### Security Considerations

* Use `yaml.safe_load` and validate rule structures.
* Avoid executing or importing scanned files.
* Design regexes to prevent ReDoS and optionally leverage `re2`.
* Run within a minimal, non‑root Docker container and log only necessary
  information.

## Engineering Requirements and Implementation Plan

Development is organized into four sprints:

1. **Sprint 1 – Project Foundation and Core Scanning**
   * Set up project skeleton, Typer CLI, basic rule loader, and single‑provider
     scanning.
2. **Sprint 2 – Multi‑Provider Support and Improved Reporting**
   * Add Azure/GCP rules, structured JSON output, severity handling, and basic
     performance improvements.
3. **Sprint 3 – SARIF Reporting and Configuration Management**
   * Implement SARIF output, external YAML config loading, logging, and
     security mitigations.
4. **Sprint 4 – Testing, Hardening, and Release Prep**
   * Comprehensive testing, documentation, security auditing, and release of
     v1.0.0.

These stages ensure a maintainable and secure CLI that provides CI/CD
observability into potential cloud resource takeover vectors.

