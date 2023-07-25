import os
import requests

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin

url = "https://tululu.org/txt.php"

os.makedirs('books', exist_ok=True)
os.makedirs('imgs', exist_ok=True)


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
    Args:
        url (str): Cсылка на текст, который хочется скачать.
        filename (str): Имя файла, с которым сохранять.
        folder (str): Папка, куда сохранять.
    Returns:
        str: Путь до файла, куда сохранён текст.
    """
    response = requests.get(url)
    response.raise_for_status()
    try:
        check_for_redirect(response)
    except requests.HTTPError:
        return

    filename = sanitize_filename(filename)
    path = os.path.join(folder, filename)
    with open(path, 'wb') as file:
        file.write(response.content)


def download_image(url, filename, folder='imgs/'):
    """Функция для скачивания текстовых файлов.
        Args:
            url (str): Cсылка на изображение, который хочется скачать.
            filename (str): Имя файла, с которым сохранять.
            folder (str): Папка, куда сохранять.
        Returns:
            str: Путь до файла, куда сохранено изображение.
        """
    response = requests.get(url)
    response.raise_for_status()

    filename = sanitize_filename(filename)
    path = os.path.join(folder, filename)
    with open(path, 'wb') as file:
        file.write(response.content)


def download_book(book_id):
    params = {
        "id": book_id,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    try:
        check_for_redirect(response)
    except requests.HTTPError:
        return

    filename = f'id{book_id}.txt'
    with open(f'books/{filename}', 'wb') as file:
        file.write(response.content)


if __name__ == '__main__':
    for book_id in range(1, 10):
        book_url = f'https://tululu.org/b{book_id}/'
        book_download_url = f'https://tululu.org/txt.php?id={book_id}'

        # get book title
        response = requests.get(book_url)
        response.raise_for_status()
        try:
            check_for_redirect(response)
        except requests.HTTPError:
            continue

        soup = BeautifulSoup(response.text, 'lxml')

        title = soup.find('div', id='content').find('h1').text
        book_title, author_name = title.split('::')
        book_title = book_title.strip()
        author_name = author_name.strip()

        # get book image
        img_path = soup.find('div', class_='bookimage').find('img')['src']
        img_url = urljoin(book_url, img_path)
        img_name = img_path.split('/')[-1]

        download_image(url, img_name, folder='imgs/')

        # get book text
        #filename = f'{book_id}. {book_title}.txt'
        #download_txt(book_download_url, filename)
        print(img_url)


