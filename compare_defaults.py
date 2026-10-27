"""Shows where the two libraries behave differently out of the box.
Run the server first:  python server.py"""
import asyncio, time
import requests, httpx

BASE = "http://127.0.0.1:8765"

def timed(label, fn):
    start = time.perf_counter()
    try:
        result = fn()
    except Exception as error:
        result = f"{type(error).__name__}"
    print(f"{label:<44} -> {result}  ({time.perf_counter() - start:.1f}s)")

print("1. Redirects (server answers /old with 302 to /new)")
timed("requests.get('/old')", lambda: requests.get(f"{BASE}/old").status_code)
timed("httpx.get('/old')", lambda: httpx.get(f"{BASE}/old").status_code)
timed("httpx.get('/old', follow_redirects=True)", lambda: httpx.get(f"{BASE}/old", follow_redirects=True).status_code)

print("\n2. Default timeout (server takes 6s to answer)")
timed("requests.get('/api/slow?seconds=6')", lambda: requests.get(f"{BASE}/api/slow", params={"seconds": 6}).status_code)
timed("httpx.get('/api/slow?seconds=6')", lambda: httpx.get(f"{BASE}/api/slow", params={"seconds": 6}).status_code)

print("\n3. Ten requests that each take 0.5s on the server")
def sequential_requests():
    for _ in range(10):
        requests.get(f"{BASE}/api/slow", params={"seconds": 0.5})
    return "10 done"
async def concurrent_httpx():
    async with httpx.AsyncClient(base_url=BASE) as client:
        await asyncio.gather(*[client.get("/api/slow", params={"seconds": 0.5}) for _ in range(10)])
    return "10 done"
timed("requests, one after another", sequential_requests)
timed("httpx.AsyncClient + asyncio.gather", lambda: asyncio.run(concurrent_httpx()))

print("\n4. Base class to catch 'any HTTP library error'")
print("requests:", requests.RequestException.__mro__[1].__name__, "-> catch requests.RequestException")
print("httpx   :", httpx.HTTPError.__mro__[1].__name__, "-> catch httpx.HTTPError (HTTPStatusError is NOT requests.HTTPError)")
