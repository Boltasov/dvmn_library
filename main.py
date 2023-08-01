import os
import time
import requests
import argparse
import logging

from bs4 import BeautifulSoup
from pathvalidate import sanitize_filename
from urllib.parse import urljoin


def check_for_redirect(response):
    if response.history:
        raise requests.HTTPError


def safe_get(url, params=None):
    while True:
        try:
            response = requests.get(url, params)
            response.raise_for_status()
            return response
        except requests.ConnectionError as e:
            logging.error('Ошибка соединения' + str(e))
            time.sleep(5)


def download_txt(url, filename, folder='books/'):
    """Функция для скачивания текстовых файлов.
        Args:
            url (str): Cсылка на текст, который хочется скачать.
            filename (str): Имя файла, с которым сохранять.
            book_id (int): id книги, которую нужно скачать.
            folder (str): Папка, куда сохранять.
        Returns:
            str: Путь до файла, куда сохранён текст.
    """
    # params = {'id': book_id}

    response = safe_get(url)
    check_for_redirect(response)

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
    response = safe_get(url)
    check_for_redirect(response)

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

    title = soup.select_one('div#content h1').text
    book_title, author_name = title.split('::')

    #img_path = soup.find('div', class_='bookimage').find('img')['src']
    img_path = soup.select_one('div.bookimage img')['src']

    comment_blocks = soup.select('div.texts')
    comments = [comment.select_one('span').text for comment in comment_blocks]

    genre_blocks = soup.select_one('span.d_book').select('a')
    genres = [genre.text for genre in genre_blocks]

    text_path = soup.find('a', string='скачать txt')
    if text_path:
        text_path = text_path['href']

    book = {
        'title': book_title.strip(),
        'author_name': author_name.strip(),
        'img_path': img_path,
        'img_name': img_path.split('/')[-1],
        'comments': comments,
        'genres': genres,
        'text_path': text_path
    }

    return book


def main():
    parser = argparse.ArgumentParser(
        prog='BookParser',
        description='Скрипт загружает книги в указанном диапазоне id с сайта tululu.org',
    )
    parser.add_argument("start_id", help='ID книги, с которой начнём парсить', type=int)
    parser.add_argument("end_id", help='ID книги, на которой закончим парсить', type=int)
    args = parser.parse_args()

    os.makedirs('books', exist_ok=True)
    os.makedirs('imgs', exist_ok=True)

    page_base_url = 'https://tululu.org/'
    download_base_url = 'https://tululu.org/txt.php'

    for book_id in range(args.start_id, args.end_id+1):
        book_page_url = urljoin(page_base_url, f'b{book_id}/')

        try:
            response = safe_get(book_page_url)
        except requests.HTTPError as e:
            logging.error(f'HTTPError для ссылки {book_page_url}\n {str(e)}')
            continue

        try:
            check_for_redirect(response)
        except requests.HTTPError as e:
            logging.error(f'Книга не найдена. id: {book_id}\n {str(e)}')
            continue

        book = parse_book_page(response.text)

        img_url = urljoin(book_page_url, book['img_path'])
        try:
            download_image(img_url, book['img_name'], folder='imgs/')
        except requests.HTTPError as e:
            logging.error(f'Изображение не найдено\n' + str(e))

        filename = f'{book_id}. {book["title"]}.txt'
        download_text_url = urljoin(download_base_url, f'?id={book_id}')
        try:
            download_txt(download_text_url, filename)
        except requests.HTTPError as e:
            logging.error(f'Текст книги не найден. id: {book_id}\n' + str(e))


if __name__ == '__main__':
    main()
