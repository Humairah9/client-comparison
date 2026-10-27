import requests

BASE_URL = "http://127.0.0.1:8765"
TIMEOUT = 1  # requests has no default timeout, so it has to be passed on every call


def make_session(token):
    session = requests.Session()
    session.headers["Authorization"] = f"Bearer {token}"
    return session


def list_books(session, author):
    response = session.get(f"{BASE_URL}/api/books", params={"author": author}, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


def create_loan(session, book_id, member_id):
    response = session.post(f"{BASE_URL}/api/loans", json={"book_id": book_id, "member_id": member_id}, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


def main():
    with make_session("demo-token") as session:
        print("books by Ines Marlowe:", [b["title"] for b in list_books(session, "Ines Marlowe")])
        print("created loan:", create_loan(session, 1, 7)["loan_id"])
        try:
            session.get(f"{BASE_URL}/api/books/999", timeout=TIMEOUT).raise_for_status()
        except requests.HTTPError as error:
            print("missing book -> handled:", error.response.status_code)
        try:
            session.get(f"{BASE_URL}/api/slow", params={"seconds": 3}, timeout=TIMEOUT)
        except requests.Timeout:
            print("slow endpoint -> handled: timeout")


if __name__ == "__main__":
    main()
