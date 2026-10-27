# Reproducing the evidence

```
python -m venv .venv && source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python server.py &                  # local test server on 127.0.0.1:8765 (Windows: run in a second terminal)
python example_requests.py          # the same tiny client written with requests
python example_httpx.py             # ...and with httpx
python compare_defaults.py          # redirects, default timeouts, async, exception base classes
python collect_evidence.py          # PyPI + git history numbers (needs internet)
bash measure_install.sh             # install size and dependencies (macOS/Linux/Git Bash)
```

Python 3.12 was used. Evidence dates are 27 October 2026; later runs will show newer numbers.
