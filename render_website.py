import json
import os

from livereload import Server
from jinja2 import Environment, FileSystemLoader, select_autoescape
from more_itertools import chunked


def build_page():
    env = Environment(
        loader=FileSystemLoader('.'),
        autoescape=select_autoescape(['html', 'xml'])
    )

    template = env.get_template('template.html')

    with open('books.txt') as books_file:
        books = json.load(books_file)

    book_pairs = list(chunked(books, 2))

    rendered_page = template.render(
        book_pairs=book_pairs,
        imgs_path=f'imgs{os.sep}',
        books_path=f'books{os.sep}',
    )

    with open('index.html', 'w', encoding="utf8") as file:
        file.write(rendered_page)


build_page()

server = Server()
server.watch('template.html', build_page)
server.serve(root='.')
