"""Collects the maintenance evidence used in README.md.
Needs network access to pypi.org and github.com (git clone, not the GitHub API).
Usage: python collect_evidence.py > evidence/maintenance.txt"""
import json, subprocess, tempfile, urllib.request, collections, os

SINCE = "2026-07-27"      # 90 days before the evidence date, 2026-10-27
YEAR_START = "2026-01-01"
PACKAGES = {"requests": "psf/requests", "httpx": "encode/httpx", "httpx2": "pydantic/httpx2"}

def pypi(name):
    req = urllib.request.Request(f"https://pypi.org/pypi/{name}/json", headers={"User-Agent": "library-comparison-task"})
    return json.load(urllib.request.urlopen(req, timeout=30))

def git(repo, *args):
    return subprocess.run(["git", "-C", repo, *args], capture_output=True, text=True).stdout.strip()

print("# Evidence collected for the evidence date 2026-10-27\n")
for name, slug in PACKAGES.items():
    data = pypi(name); info = data["info"]
    releases = sorted((min(f["upload_time"] for f in files), version) for version, files in data["releases"].items() if files)
    stable = [(t, v) for t, v in releases if not any(c.isalpha() for c in v)]
    print(f"## {name}")
    print(f"PyPI latest stable: {info['version']}  requires_python: {info['requires_python']}  licence: {info.get('license_expression') or info.get('license')}")
    print("runtime dependencies:", [r.split(';')[0].strip() for r in info['requires_dist'] if 'extra ==' not in r])
    print("newest stable upload:", stable[-1], "| newest upload of any kind:", releases[-1])
    print("stable releases since 2024-10-27:", len([1 for t, v in stable if t >= "2024-10-27"]))
    print("releases per month (all kinds, last 6 months with releases):", dict(list(collections.Counter(t[:7] for t, _ in releases).items())[-6:]))
    with tempfile.TemporaryDirectory() as tmp:
        repo = os.path.join(tmp, "r.git")
        subprocess.run(["git", "clone", "-q", "--filter=blob:none", "--bare", f"https://github.com/{slug}.git", repo], check=True)
        print("git: total commits:", git(repo, "rev-list", "--count", "HEAD"))
        print("git: latest commit on default branch:", git(repo, "log", "-1", "--format=%ad | %an | %s", "--date=short"))
        print(f"git: default-branch commits since {SINCE}:", git(repo, "rev-list", "--count", f"--since={SINCE}", "HEAD"),
              "| of which by bots:", sum(1 for a in git(repo, "log", f"--since={SINCE}", "--format=%an", "HEAD").splitlines() if "[bot]" in a))
        print(f"git: default-branch commits in 2026 (since {YEAR_START}):", git(repo, "rev-list", "--count", f"--since={YEAR_START}", "HEAD"))
        print(f"git: commits on ALL branches since {SINCE}:", git(repo, "rev-list", "--all", "--count", f"--since={SINCE}"),
              "| distinct authors:", len(set(git(repo, "log", "--all", f"--since={SINCE}", "--format=%an").splitlines())))
        print("git: most recently updated branches:", git(repo, "for-each-ref", "--sort=-committerdate", "--count=3", "--format=%(committerdate:short) %(refname:short)", "refs/heads").replace("\n", " ; "))
    print()
