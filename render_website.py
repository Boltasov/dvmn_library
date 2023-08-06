import json
import os

from jinja2 import Environment, FileSystemLoader, select_autoescape

env = Environment(
    loader=FileSystemLoader('.'),
    autoescape=select_autoescape(['html', 'xml'])
)

template = env.get_template('template.html')

with open('books.txt') as books_file:
    books = json.load(books_file)

print(books)

rendered_page = template.render(
    books=books,
    imgs_path=f'imgs/'
)

with open('index.html', 'w', encoding="utf8") as file:
    file.write(rendered_page)
