import os
import requests
import argparse

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin

os.makedirs('books', exist_ok=True)
os.makedirs('imgs', exist_ok=True)


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def download_txt(url, filename, book_id, folder='books/'):
    """Функция для скачивания текстовых файлов.
        Args:
            url (str): Cсылка на текст, который хочется скачать.
            filename (str): Имя файла, с которым сохранять.
            book_id (int): id книги, которую нужно скачать.
            folder (str): Папка, куда сохранять.
        Returns:
            str: Путь до файла, куда сохранён текст.
    """
    params = {'id': book_id}

    response = requests.get(url, params=params)
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
    try:
        check_for_redirect(response)
    except requests.HTTPError:
        return

    filename = sanitize_filename(filename)
    path = os.path.join(folder, filename)
    with open(path, 'wb') as file:
        file.write(response.content)


def parse_book_page(page_html):
    """Функция для получения данных книги из страницы книги .
        Args:
            page_html (str): HTML-код страницы книги.
        Returns:
            dict: Параметры книги.
    """
    soup = BeautifulSoup(page_html, 'lxml')
    book = {}

    title = soup.find('div', id='content').find('h1').text
    book_title, author_name = title.split('::')
    book['title'] = book_title.strip()
    book['author_name'] = author_name.strip()

    # get book image path and name
    img_path = soup.find('div', class_='bookimage').find('img')['src']
    book['img_path'] = img_path
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

    page_base_url = 'https://tululu.org/'
    download_base_url = 'https://tululu.org/txt.php'

    for book_id in range(args.start_id, args.end_id+1):
        book_page_url = urljoin(page_base_url, f'b{book_id}/')

        # get book html
        response = requests.get(book_page_url)
        response.raise_for_status()
        try:
            check_for_redirect(response)
        except requests.HTTPError:
            continue

        book = parse_book_page(response.text)

        # download book image
        img_url = urljoin(book_page_url, book['img_path'])
        download_image(img_url, book['img_name'], folder='imgs/')

        # download book text
        filename = f'{book_id}. {book["title"]}.txt'
        download_txt(download_base_url, filename, book_id)
