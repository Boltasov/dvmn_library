import os

import requests

url = "https://tululu.org/txt.php"

os.makedirs('books', exist_ok=True)


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


if __name__ == '__main__':
    for book_id in range(1, 10):
        params = {
            "id": book_id,
        }
        response = requests.get(url, params=params)
        response.raise_for_status()
        try:
            check_for_redirect(response)
        except requests.HTTPError:
            continue

        filename = f'id{book_id}.txt'
        with open(f'books/{filename}', 'wb') as file:
            file.write(response.content)
