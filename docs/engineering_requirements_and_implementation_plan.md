# Engineering Requirements and Implementation Plan

Using the product requirements and architectural design (with security considerations in mind), the implementation is broken down into **two-week sprints**.  
Each sprint delivers incremental functionality with **design, testing, and security steps**, ensuring the **core features are built first** and hardened before release.

---

## Sprint 1 – Project Foundation and Core Scanning

**Goal:**  
Set up the **project structure**, implement **basic file scanning with a simple rule**, and **prove the concept on AWS S3** as the first provider.

### Project Setup
- Initialize Git repository and Python project structure (`pyproject.toml`, `src/` layout)  
- Configure **linters and formatters** (Black, Ruff)  
- Setup **basic CI workflow** (GitHub Actions) to run **tests and linters**  
- Reference: [Medium](https://medium.com/@Mr_Pepe/setting-your-python-project-up-for-success-in-2024-365e53f7f31e)

### CLI Scaffolding
- CLI entry point using **Typer**  
- Options:  
  - `--cache-dir` (required)  
  - `--config` (optional YAML rules)  
  - `--json-out` / `--sarif-out` (optional output files)  
- Unit tests for CLI parsing using Typer utilities

### Default Rule Implementation (AWS S3)
- Create `rules_default.yaml` with initial AWS S3 regex:  
  ```regex
  ([A-Za-z0-9\-_\.]+)\.s3\.amazonaws\.com
  ```
- Load rules with `yaml.safe_load` ([Dev.to](https://dev.to/fkkarakurt/be-careful-when-using-yaml-in-python-there-may-be-security-vulnerabilities-3cdb))

### Scanning Engine (Initial)
- Implement `Scanner.scan_directory(path)`:
  - Recurse with `path.rglob('*')`  
  - Open text files, line-by-line scan against rules  
  - Collect findings with filename, line number, snippet  
  - Handle errors gracefully (skip unreadable files)

### Basic Output
- Print findings or generate rudimentary JSON output  
- Validate detection using test file: `http://test.s3.amazonaws.com/file`

### Testing & Validation
- Unit tests for `load_rules()` with safe YAML  
- Integration test with dummy S3 URLs  
- Confirm CLI works and package installs locally

**Deliverable:**  
A minimal **end-to-end working scanner** detecting AWS S3 references.

---

## Sprint 2 – Multi-Provider Support and Improved Reporting

**Goal:**  
Expand support to **Azure & GCP**, implement **JSON output**, and add **severity classification**.

### Expand Rule Set
- Add regex for:  
  - **Azure Blob Storage**: `([A-Za-z0-9-]+)\.blob\.core\.windows\.net`  
  - **GCP Storage**: `storage\.googleapis\.com/[A-Za-z0-9\-._]+`  
  - **CloudFront/CDN** domains as optional checks
- Assign **severity** (S3/Azure = High, GCP = Medium)

### JSON Output
- Implement `ReportGenerator.to_json()` producing:
```json
{
  "scanned_directory": "...",
  "timestamp": "...",
  "findings": [
     {
       "file": "path/to/file",
       "line": 123,
       "match": "http://bad.bucket.s3.amazonaws.com/...",
       "rule_id": "AWS.S3.Takeover",
       "description": "Potential AWS S3 bucket takeover point",
       "severity": "HIGH"
     }
  ]
}
```

### Severity Handling
- Track highest severity found  
- Optional `--fail-on` CLI flag to exit with non-zero on high severity findings

### Performance Improvements
- Introduce **multithreading** with `ThreadPoolExecutor`  
- Streamline large file scanning; handle Unicode gracefully  
- Optional skip for files >50MB

### Testing
- Unit tests for rules merging & severity tagging  
- Test JSON output and multi-provider detection  
- Stress test with many files to ensure stable performance

**Deliverable:**  
Tool supports **AWS, Azure, GCP**, structured **JSON output**, and **basic severity tagging**.

---

## Sprint 3 – SARIF Reporting and Configuration Management

**Goal:**  
Add **SARIF output**, **external YAML rules support**, and finalize **logging & exit codes**.

### SARIF Output Implementation
- Use [simple-sarif](https://pypi.org/project/simple-sarif/)  
- Populate SARIF with:  
  - Tool metadata  
  - Rules (id, description, severity)  
  - Results with file URI & line number  
- Map severity → SARIF: High=error, Medium=warning, Low=note

### External YAML Config
- Load user-supplied `--config` rules with `yaml.safe_load`  
- Replace or merge with defaults (v1.0 uses replace for simplicity)  
- Validate regex and rule structure

### Logging & Exit Codes
- Add `--verbose` for INFO/DEBUG output  
- Exit codes:  
  - 0 = Success / no high findings  
  - 1 = High severity found (if `--fail-on high`)  
  - 2+ = Execution error  

### Security Hardening
- Confirm `safe_load` use ([Dev.to](https://dev.to/fkkarakurt/be-careful-when-using-yaml-in-python-there-may-be-security-vulnerabilities-3cdb))  
- Optionally switch to RE2 ([Semgrep](https://semgrep.dev/docs/writing-rules/rule-ideas))  
- Add file size cutoff & error handling

**Deliverable:**  
Feature-complete **v1.0.0** with:  
- SARIF + JSON outputs  
- Configurable YAML rules  
- Security mitigations aligned with the **Threat Model**

---

## Sprint 4 – Testing, Hardening, and Release Prep

**Goal:**  
Perform **full testing, security review, and release prep**.

### Comprehensive Testing
- Cross-platform verification (Linux primary, Windows optional)  
- Scan large real-world package cache for performance profiling  
- Integration testing of JSON & SARIF outputs

### Security Audit
- Run **Bandit** for Python static security checks  
- Validate dependencies are pinned & updated  
- Review threat model coverage

### Release Prep
- Increment version to `v1.0.0`  
- Build and validate **Docker image** (non-root user, minimal base)  
- Optional **PyPI release** for Python install users  
- Document usage examples & CI integration

**Deliverable:**  
A **polished, secure, and documented v1.0.0 release**, ready for **CI/CD integration**.

---

## Summary

By following this **four-sprint plan**, we ensure:  
- Product requirements are fully met  
- Architecture is modular and maintainable  
- Security is embedded from the start  
- The tool is **CI/CD-ready**, extensible, and positioned for **future enhancements**
