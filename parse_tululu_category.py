import os
import json
import requests
import logging

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
        
        books = soup.find_all('table', class_='d_book')

        for book in books:
            book_path = book.find('a')['href']
            # book_id = "".join(symbol for symbol in book_path if symbol.isdecimal())
            book_url = urljoin(base_url, book_path)
            # book_id_url = {"id": book_id, "url": book_url}
            # book_id_urls.append(book_id_url)
            book_urls.append(book_url)
        
    return book_urls


if __name__ == '__main__':
    book_urls = parse_book_urls()
    base_url = 'https://tululu.org/'

    os.makedirs('books', exist_ok=True)
    os.makedirs('imgs', exist_ok=True)

    for book_url in book_urls:
        response = requests.get(book_url)
        response.raise_for_status()

        book = parse_book_page(response.text)

        books_file = open("books.txt", "a")

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

            book_json = json.dumps(book, ensure_ascii=False, indent=4)

            books_file.write(book_json)
            books_file.close()

            print(f'{book["title"]}')
