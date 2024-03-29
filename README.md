### [![Typing SVG](https://readme-typing-svg.herokuapp.com?color=%2336BCF7&lines=Парсер+документации+Python+и+PEP)](https://git.io/typing-svg)
# Описание
Парсер информации о python с **https://docs.python.org/3/** и **https://peps.python.org/**
### Перед использованием
Клонируйте репозиторий к себе на компьютер:

```
git clone https://github.com/94R1K/bs4_parser_pep.git
```

В корневой папке создайте виртуальное окружение и установите зависимости.
```
python -m venv venv
```

```
pip install -r requirements.txt
```

### Перейдите в директорию ./src/

```
cd src/
```

### Запустите файл main.py выбрав необходимый парсер и аргументы(приведены ниже)

```
python main.py [вариант парсера] [аргументы]
```

### Встроенные парсеры
- whats-new   
Парсер выводящий спсок изменений в python.

```
python main.py whats-new [аргументы]
```

- latest_versions
Парсер выводящий список версий python и ссылки на их документацию.

```
python main.py latest-versions [аргументы]
```

- download   
Парсер скачивающий zip архив с документацией python в pdf формате.

```
python main.py download [аргументы]
```

- pep
Парсер выводящий список статусов документов pep
и количество документов в каждом статусе. 

```
python main.py pep [аргументы]
```

### Аргументы
Есть возможность указывать аргументы для изменения работы программы:   
- -h, --help
Общая информация о командах.

```
python main.py -h
```

- -c, --clear-cache
Очистка кеша перед выполнением парсинга.

```
python main.py [вариант парсера] -c
```

- -o {pretty,file}, --output {pretty,file}   
Дополнительные способы вывода данных   
pretty - выводит данные в командной строке в таблице   
file - сохраняет информацию в формате csv в папке ./results/

```
python main.py [вариант парсера] -o file
```

# Об авторе
Лошкарев Ярослав Эдуардович \
Python-разработчик (Backend) \
Россия, г. Москва \
E-mail: real-man228@yandex.ru 

[![VK](https://img.shields.io/badge/Вконтакте-%232E87FB.svg?&style=for-the-badge&logo=vk&logoColor=white)](https://vk.com/yalluv)
[![TG](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/yallluv)
