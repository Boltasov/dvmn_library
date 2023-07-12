import requests

url = "https://tululu.org/txt.php"

for i in range(1, 10):
    params = {
        "id": i,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()

    filename = f'id{i}.txt'
    with open(filename, 'wb') as file:
        file.write(response.content)
