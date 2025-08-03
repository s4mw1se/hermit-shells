 # Hermit Shells

 Cloud Resource Takeover Scanner

 ## Prerequisites

 - Python 3.11+
 - pip
 - Docker (for containerized usage)
 - Git (for cloning the repository)

 ## Installation

 You can install the scanner from PyPI or from source.

 ### From PyPI

 ```fish
 pip install hermit-shells
 ```

 ### From Source

 ```fish
 git clone https://github.com/s4mw1se/hermit-shells.git
 cd hermit-shells
 pip install -e .
 ```

 ## Usage

 Scan a directory for cloud resource takeover patterns:

 ```fish
 scanner scan \
   --cache-dir /path/to/cache \
   [--config /path/to/rules.yaml] \
   [--json-out report.json] \
   [--sarif-out report.sarif] \
   [--fail-on HIGH|MEDIUM|LOW] \
   [-v]
 ```

 **Options**:
 - `--cache-dir` : Directory to scan (required)
 - `--config`    : External YAML rules file (optional)
 - `--json-out`  : Output JSON file path (optional)
 - `--sarif-out` : Output SARIF file path (optional)
 - `--fail-on`   : Fail on severity level (HIGH, MEDIUM, LOW)
 - `-v, --verbose`: Enable verbose logging

 ## Docker

 A sample `Dockerfile` for containerized usage:

 ```dockerfile
 FROM python:3.11-slim

 WORKDIR /app

 COPY . .

 RUN pip install --no-cache-dir .

 ENTRYPOINT ["scanner"]
 ```

 Build and run the container:

 ```fish
 docker build -t hermit-shells .
 docker run --rm -v /path/to/cache:/cache hermit-shells scan --cache-dir /cache --json-out /cache/report.json --sarif-out /cache/report.sarif
 ```

 ## CI/CD

 A sample GitHub Actions workflow (`.github/workflows/ci.yml`):

 ```yaml
 name: CI

 on:
   push:
     branches: [ main ]
   pull_request:
     branches: [ main ]

 jobs:
   test:
     runs-on: ubuntu-latest

     steps:
       - uses: actions/checkout@v3
       - name: Set up Python
         uses: actions/setup-python@v4
         with:
           python-version: 3.11
       - name: Install dependencies
         run: pip install -e .
       - name: Run tests
         run: pytest
       - name: Run scanner
         run: |
           scanner scan --cache-dir . --json-out report.json --sarif-out report.sarif
 ```

 ## Contributing

 Contributions are welcome! Please open issues and pull requests on GitHub.

 ## License

 MIT License
