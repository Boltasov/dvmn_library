import os
import requests
import argparse

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


def parse_book_page(page_html):
    soup = BeautifulSoup(page_html, 'lxml')
    book = {}

    title = soup.find('div', id='content').find('h1').text
    book_title, author_name = title.split('::')
    book['book_title'] = book_title.strip()
    book['author_name'] = author_name.strip()

    # get book image
    img_path = soup.find('div', class_='bookimage').find('img')['src']
    book['img_url'] = urljoin(book_url, img_path)
    book['img_name'] = img_path.split('/')[-1]

    # get comments
    comments = []
    comment_blocks = soup.find_all('div', class_='texts')
    for comment in comment_blocks:
        comments.append(comment.find('span').text)
    book['comments'] = comments

    # get genres
    genres = []
    genre_blocks = soup.find('span', class_='d_book').find_all('a')
    for genre in genre_blocks:
        genres.append(genre.text)
    book['genres'] = genres

    return book


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("start_id", help='ID книги, с которой начнём парсить', type=int)
    parser.add_argument("end_id", help='ID книги, на которой закончим парсить', type=int)
    args = parser.parse_args()

    for book_id in range(args.start_id, args.end_id+1):
        book_url = f'https://tululu.org/b{book_id}/'
        book_download_url = f'https://tululu.org/txt.php?id={book_id}'

        # get book html
        response = requests.get(book_url)
        response.raise_for_status()
        try:
            check_for_redirect(response)
        except requests.HTTPError:
            continue

        book = parse_book_page(response.text)

        #download_image(url, img_name, folder='imgs/')

        # get book text
        #filename = f'{book_id}. {book_title}.txt'
        #download_txt(book_download_url, filename)

        print(book_id)
        print(book)


