import os

import requests

url = "https://tululu.org/txt.php"

os.makedirs('books', exist_ok=True)

for i in range(1, 10):
    params = {
        "id": i,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()

    filename = f'id{i}.txt'
    with open(f'books/{filename}', 'wb') as file:
        file.write(response.content)
