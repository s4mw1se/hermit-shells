# Architectural Design Requirements Document

## Overview of the Solution Architecture
The **Cloud Resource Takeover Scanner** is a **command-line Python application** designed with **modular components** for maintainability and clarity.

**Key Components:**
1. **CLI Interface** – Parses input arguments (directory path, output file options, config path) and triggers scanning.  
2. **Core Scanning Engine** – Walks through files, applies regex rules, and records findings.  
3. **Rules Management** – Loads default rules (internal YAML) and optional user-supplied rules, compiles patterns.  
4. **Reporting/Output Module** – Generates JSON and SARIF reports.  
5. **Logging & Utilities** – Supports concurrency, file filtering, and error handling.  

This design follows **separation of concerns**, making the tool **easier to test and extend** (e.g., adding new output formats or rule types).

---

## Key Design Principles

### 1. Modularity & Maintainability
- Classes and modules for clear separation:
  - `Scanner` – scanning logic  
  - `Rule` – represents individual rule  
  - `ReportGenerator` – generates JSON & SARIF  
- Extendable without modifying core logic.

### 2. Modern Python Features
- **Python 3.11+** best practices:
  - **Type hints** for static analysis ([Stuart Ellis](https://www.stuartellis.name/articles/python-modern-practices/))  
  - **Data classes** for structured findings ([Stuart Ellis](https://www.stuartellis.name/articles/python-modern-practices/))  
  - **Enums** for severity levels ([Stuart Ellis](https://www.stuartellis.name/articles/python-modern-practices/))  
  - **f-strings** for concise formatting

### 3. Project Structure (src layout)
```plaintext
cloud-takeover-scanner/
├── src/cloud_takeover_scanner/
│   ├── __init__.py
│   ├── cli.py           # CLI entry point
│   ├── scanner.py       # Core scanning logic
│   ├── rules.py         # Rule management
│   ├── report.py        # JSON/SARIF output
│   └── rules_default.yaml
├── tests/
├── pyproject.toml        # Project metadata & dependencies
├── README.md
└── Dockerfile
```
- `pyproject.toml` ensures modern build (Setuptools/Hatch/Poetry) ([Medium](https://medium.com/@Mr_Pepe/setting-your-python-project-up-for-success-in-2024-365e53f7f31e))  
- Tests live in `tests/` for CI compatibility.

### 4. Library Choices
- **CLI Parsing:** [Typer](https://medium.com/@yuxuzi/mastering-python-command-line-tools-top-5-libraries-in-2024-e5bab46c1e7b) (modern, type hint-based)  
- **YAML Parsing:** [PyYAML safe_load](https://dev.to/fkkarakurt/be-careful-when-using-yaml-in-python-there-may-be-security-vulnerabilities-3cdb)  
- **Regex Matching:** Python `re` (compiled), optional [RE2](https://semgrep.dev/docs/writing-rules/rule-ideas) for ReDoS protection  
- **SARIF Output:** [simple-sarif](https://pypi.org/project/simple-sarif/)  

### 5. File Scanning Logic
- Recursively scans directories with `pathlib.Path.rglob()` ([Stuart Ellis](https://www.stuartellis.name/articles/python-modern-practices/))  
- Opens files in text mode with fallback encodings (UTF-8 → Latin-1)  
- Line-by-line regex matching to capture filename, line number, matched snippet, and severity  
- **Concurrency:** Thread pool for I/O-bound scanning; optional multi-processing for CPU-heavy regex.

### 6. Output Generation
- **JSON:** Structured findings with metadata  
- **SARIF:** Includes rules, results, severity mapped to SARIF levels (error/warning/note) ([PyPI](https://pypi.org/project/simple-sarif/))  
- Proper file closing and JSON escaping to prevent malformed reports.

---

## Configuration & Extensibility
- External **YAML rules** allow custom patterns & severities.  
- Rules loaded at runtime:
  1. Default internal YAML  
  2. Optional external file (merge/override by ID)  
- Invalid YAML or regex is reported with **clear errors**.  

---

## Security & Performance Considerations

### Security
- **Safe YAML parsing** ([Dev.to](https://dev.to/fkkarakurt/be-careful-when-using-yaml-in-python-there-may-be-security-vulnerabilities-3cdb))  
- **Regex DoS mitigation** using RE2 or safe patterns ([Semgrep](https://semgrep.dev/docs/writing-rules/rule-ideas))  
- **Non-root Docker execution** and minimal base image  
- **Read-only scanning**; no file modification or execution  

### Performance
- **Stream files line-by-line** to reduce memory usage  
- **Multi-threaded scanning** for I/O efficiency  
- Handles **large directories quickly** without CI bottlenecks  

---

## Summary
- Clear, modular architecture using modern Python  
- Data-driven scanning with YAML-based rule management  
- Secure, CI/CD-friendly design with SARIF & JSON outputs  
- Extensible for future cloud providers and output formats
