# Product Requirements Document (v1.0.0)

## Vision and Background
The goal of this CLI tool is to **enhance software supply chain security** by detecting potential **cloud resource takeover vulnerabilities** in third-party packages.

Recent incidents have shown that attackers can hijack **orphaned cloud resources** (like S3 buckets or Azure storage endpoints) to serve malicious code without altering the package itself ([Checkmarx](https://checkmarx.com/blog/hijacking-s3-buckets-new-attack-technique-exploited-in-the-wild-by-supply-chain-attackers/)).  

For example, versions of the **NPM package `bignum`** were compromised after an AWS S3 bucket (used to host binaries) was deleted and subsequently taken over by an attacker ([Checkmarx](https://checkmarx.com/blog/hijacking-s3-buckets-new-attack-technique-exploited-in-the-wild-by-supply-chain-attackers/)).  

Similarly, researchers found dozens of packages and subdomains vulnerable to such “dangling DNS” or cloud resource takeovers in the wild ([Checkmarx](https://checkmarx.com/blog/hijacking-s3-buckets-new-attack-technique-exploited-in-the-wild-by-supply-chain-attackers/), [SentinelOne](https://www.sentinelone.com/blog/re-assessing-risk-subdomain-takeovers-as-supply-chain-attacks/)).  

In late 2024, researchers took control of ~150 abandoned S3 buckets and observed **over 8 million artifact requests**, including container images and software updates ([SentinelOne](https://www.sentinelone.com/blog/re-assessing-risk-subdomain-takeovers-as-supply-chain-attacks/)).

> **Vision:** Provide an automated scanner that integrates into CI/CD pipelines to identify references to AWS, Azure, and GCP cloud resources that could be hijacked by attackers.

---

## Target Users and Use Case
- **Primary users:** DevSecOps engineers & security-conscious developers.  
- **Use in CI:** Mount package manager cache or artifact directories and scan non-interactively.  
- **Goal:** Generate a JSON/SARIF report for security review or automated build gating.

---

## Key Features and Requirements

### 1. Configurable Scan Directory
- Accepts a directory path (e.g., npm `node_modules`, Maven `.m2`, PyPI wheels cache).  
- Recursively scans files for **cloud resource references**.  
- Treats files as text only; **no code execution**.  
- Records **filename and line number** for each finding ([SentinelOne](https://www.sentinelone.com/blog/re-assessing-risk-subdomain-takeovers-as-supply-chain-attacks/)).

### 2. Cloud Resource Pattern Detection
Regex-based rules detect takeover-prone resources:

- **AWS:** `*.s3.amazonaws.com`, CloudFront domains ([Checkmarx](https://checkmarx.com/blog/hijacking-s3-buckets-new-attack-technique-exploited-in-the-wild-by-supply-chain-attackers/))  
- **Azure:** `*.blob.core.windows.net/<container>` and CDN endpoints  
- **GCP:** `storage.googleapis.com/<bucket>` and `<bucket>.storage.googleapis.com`  
- **Optional:** Generic cloud/CDN domains like `*.cloudfront.net` or `*.cloudapp.azure.com`  

Default rules cover **object storage, CDN endpoints, and container registries** ([SentinelOne](https://www.sentinelone.com/blog/re-assessing-risk-subdomain-takeovers-as-supply-chain-attacks/)).

### 3. Severity Classification
- **High:** Likely takeover candidates (e.g., S3 bucket names in a globally unique namespace).  
- **Medium:** Resources requiring additional conditions for takeover.  
- **Low:** Likely internal or reserved domains.  
- Severity is **rule-based** for v1.0 ([SentinelOne](https://www.sentinelone.com/blog/re-assessing-risk-subdomain-takeovers-as-supply-chain-attacks/)).

### 4. Output Formats (CI/CD Friendly)
- **JSON report** – structured findings with file, line, match, rule, severity.  
- **SARIF report** – compliant with [GitHub SARIF standard](https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/sarif-support-for-code-scanning) for integration with CI/CD.  
- SARIF generation may leverage [simple-sarif](https://pypi.org/project/simple-sarif/).  
- Tool exits **non-zero if high-severity findings** (configurable).

### 5. Non-Interactive CLI
- Runs autonomously with CLI args/env vars:  
  ```bash
  scanner --cache-dir /path/to/cache --output-json report.json --output-sarif report.sarif --config rules.yaml
  ```

### 6. Configurability and Extensibility
- Supports **external YAML rule files** for custom patterns.  
- Rules include: `id`, `pattern` (regex), `description`, `cloud_provider`, `severity`.  
- Designed for **safe YAML loading** using [`yaml.safe_load`](https://dev.to/fkkarakurt/be-careful-when-using-yaml-in-python-there-may-be-security-vulnerabilities-3cdb).

### 7. Performance and Scalability
- Efficient handling of **thousands of files**.  
- Uses **compiled regex** and optional **multi-threaded scanning**.  
- No network calls – **offline & CI-friendly**.

### 8. Platform and Environment
- **Python 3.11+**, containerized for CI/CD.  
- Minimal Docker image (non-root user).  
- Cross-platform (Linux primary).

### 9. Compliance and Standards
- Output conforms to **SARIF 2.1.0** ([GitHub Docs](https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/sarif-support-for-code-scanning)).  
- Aligned with OWASP/SLSA best practices for supply chain tools.

---

## Constraints and Assumptions
- Files are scanned as text; binary files are skipped.  
- **Read-only:** The tool never modifies files.  
- **Offline operation:** No external connectivity required.  
- Regex-based detection may yield **false positives**; security engineers validate findings.

---

## Success Criteria (v1.0.0)
- Detects AWS S3, Azure Blob, and GCP Storage takeover patterns.  
- Produces valid JSON and SARIF reports.  
- Scans typical package directories in **minutes**, not hours.  
- Robust against **file encoding issues** and large directories.  
- Passes **security review and threat model validation**.

---

### References
- [Checkmarx – Hijacking S3 Buckets](https://checkmarx.com/blog/hijacking-s3-buckets-new-attack-technique-exploited-in-the-wild-by-supply-chain-attackers/)  
- [SentinelOne – Subdomain Takeovers](https://www.sentinelone.com/blog/re-assessing-risk-subdomain-takeovers-as-supply-chain-attacks/)  
- [GitHub SARIF Standard](https://docs.github.com/en/code-security/code-scanning/integrating-with-code-scanning/sarif-support-for-code-scanning)  
- [simple-sarif – PyPI](https://pypi.org/project/simple-sarif/)  
- [Safe YAML Loading](https://dev.to/fkkarakurt/be-careful-when-using-yaml-in-python-there-may-be-security-vulnerabilities-3cdb)  
