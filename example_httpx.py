import httpx

BASE_URL = "http://127.0.0.1:8765"


def make_client(token):
    # base_url, default headers and a default timeout all live on the client
    return httpx.Client(base_url=BASE_URL, headers={"Authorization": f"Bearer {token}"}, timeout=1)


def list_books(client, author):
    response = client.get("/api/books", params={"author": author})
    response.raise_for_status()
    return response.json()


def create_loan(client, book_id, member_id):
    response = client.post("/api/loans", json={"book_id": book_id, "member_id": member_id})
    response.raise_for_status()
    return response.json()


def main():
    with make_client("demo-token") as client:
        print("books by Ines Marlowe:", [b["title"] for b in list_books(client, "Ines Marlowe")])
        print("created loan:", create_loan(client, 1, 7)["loan_id"])
        try:
            client.get("/api/books/999").raise_for_status()
        except httpx.HTTPStatusError as error:
            print("missing book -> handled:", error.response.status_code)
        try:
            client.get("/api/slow", params={"seconds": 3})
        except httpx.TimeoutException:
            print("slow endpoint -> handled: timeout")


if __name__ == "__main__":
    main()
