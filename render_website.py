import json
import os

from livereload import Server
from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked


def build_page(books, pages_dir, page):
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    book_pairs = list(chunked(books, 2))

    rendered_page = template.render(
        book_pairs=book_pairs,
        imgs_path=f'..{os.sep}imgs{os.sep}',
        books_path=f'..{os.sep}books{os.sep}',
    )

    page_path = os.path.join(pages_dir, f'index{page}.html')
    with open(page_path, 'w', encoding="utf8") as file:
        file.write(rendered_page)


def main():
    pages_dir = 'pages'
    os.makedirs(pages_dir, exist_ok=True)

    with open('books.txt') as books_file:
        books = json.load(books_file)

    books_on_pages = list(chunked(books, 20))

    for page, books_on_page in enumerate(books_on_pages, 1):
        build_page(books_on_page, pages_dir, page)

    server = Server()
    server.watch('template.html', build_page)
    server.serve(root='.')


if __name__ == '__main__':
    main()
