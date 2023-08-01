import os
import json
import requests
import logging
import argparse

from bs4 import BeautifulSoup
from urllib.parse import urljoin
from main import parse_book_page, download_txt, download_image, safe_get


def parse_book_urls(start_page, end_page):
    science_fiction_url = 'https://tululu.org/l55/'
    base_url = 'https://tululu.org/'

    book_urls = []
    for page in range(start_page, end_page):
        page_url = urljoin(science_fiction_url, f'{page}/')

        try:
            response = safe_get(page_url)
        except requests.HTTPError as e:
            logging.error(f'Страница книги не найдена.\n' + str(e))
            continue

        soup = BeautifulSoup(response.text, 'lxml')

        selector = 'table.d_book'
        books = soup.select(selector)

        for book in books:
            book_path = book.select_one('a')['href']
            book_url = urljoin(base_url, book_path)
            book_urls.append(book_url)

    return book_urls


def main():
    parser = argparse.ArgumentParser(
        prog='BookParser',
        description='Скрипт загружает книги с указанных страниц с сайта tululu.org',
    )
    parser.add_argument("--start_page", help='Номер страницы, с которой начнём парсить', type=int, required=True)
    parser.add_argument("--end_page", help='Номер страницы, на которой закончим парсить', type=int, default=701)
    parser.add_argument("--dest_folder", help='Путь к каталогу с результатами парсинга: картинкам, книгам, JSON.',
                        type=str, default='')
    parser.add_argument("--skip_imgs", help='Скачивать ли картинки', action="store_true")
    parser.add_argument("--skip_txt", help='Скачивать ли тексты книг', action="store_true")
    args = parser.parse_args()

    folder = args.dest_folder
    books_folder = os.path.join(args.dest_folder, 'books')
    img_folder = os.path.join(args.dest_folder, 'imgs')

    book_urls = parse_book_urls(args.start_page, args.end_page)

    os.makedirs(books_folder, exist_ok=True)
    os.makedirs(img_folder, exist_ok=True)

    books = []

    for book_url in book_urls:
        try:
            response = safe_get(book_url)
            book = parse_book_page(response.text)
        except requests.HTTPError as e:
            logging.error(f'Страница книги не найдена.\n' + str(e))
            continue

        if not book['text_path']:
            continue

        if not args.skip_txt:
            filename = f'{book["title"]}.txt'
            download_text_url = urljoin(book_url, book['text_path'])
            try:
                download_txt(download_text_url, filename, folder=books_folder)
            except requests.HTTPError as e:
                logging.error(f'Текст книги не найден.\n' + str(e))

        if not args.skip_imgs:
            img_url = urljoin(book_url, book['img_path'])
            try:
                download_image(img_url, book['img_name'], folder=img_folder)
            except requests.HTTPError as e:
                logging.error(f'Изображение не найдено\n' + str(e))

        books.append(book)

    with open(os.path.join(folder, 'books.txt'), 'w') as books_file:
        json.dump(books, books_file, ensure_ascii=False, indent=4)
    print('Done writing books into a file')


if __name__ == '__main__':
    main()
