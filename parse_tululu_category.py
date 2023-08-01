import os
import json
import requests
import logging
import pickle

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from main import parse_book_page, download_txt, download_image


def parse_book_urls():
    science_fiction_url = 'https://tululu.org/l55/'
    base_url = 'https://tululu.org/'

    # book_id_urls = []
    book_urls = []
    for page in range(1, 2):
        page_url = urljoin(science_fiction_url, f'{page}/')

        response = requests.get(page_url)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'lxml')

        selector = 'table.d_book'
        books = soup.select(selector)

        for book in books:
            book_path = book.select_one('a')['href']
            # book_id = "".join(symbol for symbol in book_path if symbol.isdecimal())
            book_url = urljoin(base_url, book_path)
            # book_id_url = {"id": book_id, "url": book_url}
            # book_id_urls.append(book_id_url)
            book_urls.append(book_url)
        break

    return book_urls


if __name__ == '__main__':
    book_urls = parse_book_urls()
    base_url = 'https://tululu.org/'

    os.makedirs('books', exist_ok=True)
    os.makedirs('imgs', exist_ok=True)

    books = []

    for book_url in book_urls:
        response = requests.get(book_url)
        response.raise_for_status()

        book = parse_book_page(response.text)

        if book['text_path']:
            filename = f'{book["title"]}.txt'
            download_text_url = urljoin(base_url, book['text_path'])
            try:
                download_txt(download_text_url, filename)
            except requests.HTTPError as e:
                logging.error(f'Текст книги не найден.\n' + str(e))

            img_url = urljoin(book_url, book['img_path'])
            try:
                download_image(img_url, book['img_name'], folder='imgs/')
            except requests.HTTPError as e:
                logging.error(f'Изображение не найдено\n' + str(e))

            books.append(book)

            print(f'{book["title"]}')

    books_json = json.dumps(books, ensure_ascii=False, indent=4)
    with open('books.txt', 'w') as books_file:
        books_file.write(books_json)
        print('Done writing list into a file')
