# Скачивание книг

Программа предназначена для загрузки книг с сайта https://tululu.org/.

### Как установить

Должны быть предустановлены Python 3 и pip.

Скачайте код с помощью команды в командной строке
```
git clone https://github.com/Boltasov/dvmn_library
```
Перейдите в папку с проектом
```
cd dvmn_library
```
Установите необходимые библиотеки командой
```
python pip install -r requirements.txt
```
Теперь, чтобы запустить код, используйте следующую команду, указав вместо `start_id` и `end_id` свои значения начального и конечного id загружаемых книг:
```commandline
python main.py start_id end_id
```
При успешном выполнении в этой директории будут созданы папки `books` и `imgs`, куда загрузятся книги и их изображения соответственно.

### Цель проекта

Код написан в образовательных целях на онлайн-курсе для веб-разработчиков [dvmn.org](https://dvmn.org/).