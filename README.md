# requests vs httpx: choosing an HTTP client for Python

**The need:** calling web APIs from Python. **Method:** on 27 October 2026 I compared `requests` 2.34.2 and `httpx` 0.28.1 by reading their documentation, cloning their repositories, querying PyPI, installing each in a clean virtual environment, and writing the same small client against a local test server (Python 3.12). Every number below can be regenerated with the scripts in this repository.

## Size and dependencies

| | requests | httpx |
|---|---|---|
| Packages installed with it | 4 | 6 |
| Disk (library + dependencies) | 3.6 MB | 4.6 MB |
| Wheel size | 71 KB | 72 KB |
| Python needed | 3.10+ | 3.8+ |

Both are light. They share certifi and idna; requests adds urllib3 and charset-normalizer, while httpx adds anyio, h11, httpcore and typing_extensions.

## Maintenance

**requests** is steady but quiet. The latest release, 2.34.2, is from 14 May 2026, and there were seven stable releases since October 2024. Its main branch has 117 commits in 2026, but only 10 in the last 90 days, and 9 of those are Dependabot bumps. The tracker shows 153 open issues and 88 open pull requests.

**httpx** is the harder case. Its last stable release, 0.28.1, dates from 6 December 2024, and its master branch has a single commit in 2026 (23 February). Version 1.0 is being prepared on a separate branch whose changelog still marks 1.0.0 as unreleased; the newest pre-release is 1.0.dev6 (31 August 2026). In May 2026 Pydantic published **httpx2**, a fork whose README says httpx has seen limited activity recently. I checked it: 2.16.0 was released on 21 October 2026, there have been 21 releases since May, and its main branch has 103 commits in the last 90 days.

## Documentation

The requests docs say plainly that there is no default timeout and advise setting one on nearly every call. That is honest, but four of the twelve open issues on the tracker's first page are documentation complaints, including one calling the `stream` parameter ambiguous. The httpx site has a dedicated "Requests compatibility" guide listing the differences I then ran into myself (redirects, timeouts, exception names), which is excellent for anyone arriving from requests. Its weakness is that the docs are now split between python-httpx.org and the httpx2 site.

## Writing the same example

The task: list books with a query parameter, POST JSON, handle a 404, handle a timeout, and send a bearer token on every call. The requests version is 29 lines and the httpx version 27, with identical output (`evidence/example_output.txt`).

httpx's `Client` holds the base URL, headers and timeout in one constructor, so each call is short. requests has no base URL or session-wide timeout, so every call repeats `timeout=` and builds its URL by hand. Three differences I would not have guessed, all measured:

- Redirects: a 302 gave status 200 in requests but 302 in httpx, which does not follow redirects unless told to.
- Timeouts: against a 6-second endpoint, requests waited the full 6.0 s, while httpx raised `ReadTimeout` after 5.0 s.
- Errors: the exception names differ (`requests.HTTPError` versus `httpx.HTTPStatusError`), so error handling needs rewriting when porting.

Changing one import to `httpx2` produced identical output again.

## Recommendation

Use **requests** for synchronous scripts and most services. It has the smallest dependency set, a stable API and the most familiar documentation, and it is still released, only slowly. Always pass `timeout=`.

Choose the httpx family when you need async (requests has none), HTTP/2, safe default timeouts, or tests that call ASGI/WSGI apps directly. For new work in that family I would pick **httpx2 over httpx**, because of the release and commit evidence above, accepting Python 3.11+ and a young fork backed by one company. I would revisit this if httpx ships a stable 1.0 or if requests' release pace slows further.

## Limits of this evidence

GitHub's API rate-limited my sandbox, so issue counts come from page snapshots that may lag by weeks; release and commit figures come straight from PyPI and git. It is one example on one machine, so timings are indicative only.

*Code and raw evidence: `server.py`, `example_requests.py`, `example_httpx.py`, `compare_defaults.py`, `evidence/`.*
