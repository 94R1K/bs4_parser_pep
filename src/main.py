import logging
import re
from collections import defaultdict
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEP_URL
from outputs import control_output
from utils import find_tag, get_response


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all('li',
                                              attrs={'class': 'toctree-l1'})
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, Автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = section.find('a')
        version_link = urljoin(whats_new_url, version_a_tag['href'])
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, 'lxml')
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )
    return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Ничего не нашлось')
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        text_match = re.search(pattern, a_tag.text)
        if 'All versions' in a_tag.text:
            results.append(
                (link, a_tag.text)
            )
        else:
            version, status = text_match.groups()
            results.append(
                (link, version, status)
            )
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    div_body = find_tag(soup, 'div', attrs={'role': 'main'})
    table = find_tag(div_body, 'table', attrs={'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table,
        'a',
        attrs={'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    download_dir = BASE_DIR / 'downloads'
    download_dir.mkdir(exist_ok=True)
    archive_path = download_dir / filename
    response = session.get(archive_url)

    with open(archive_path, 'wb') as file:
        file.write(response.content)
    print(filename)
    logging.info(f'Архив был загружен и сохранен: {archive_path}')


def pep(session):
    response = get_response(session, PEP_URL)
    status_count = defaultdict(int)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    section = find_tag(soup, 'section', attrs={'id': 'pep-content'})
    tables = section.find_all(
        'table',
        attrs={'class': 'pep-zero-table docutils align-default'}
    )
    results = [('Статус', 'Количество')]
    for table in tqdm(tables, desc='Парсинг PEP'):
        columns = find_tag(table, 'tbody')
        values = columns.find_all('tr')
        for value in values:
            status_column = value.find('abbr')
            if status_column is None:
                break
            status_in_column = status_column.text[1:]
            link = find_tag(
                value,
                'a',
                attrs={'class': 'pep reference internal'}
            )['href']
            pep_link = urljoin(PEP_URL, link)
            response = get_response(session, pep_link)
            if response is None:
                continue
            soup = BeautifulSoup(response.text, 'lxml')
            section = find_tag(soup, 'section', attrs={'id': 'pep-content'})
            field_list = find_tag(
                section,
                'dl',
                attrs={'class': 'rfc2822 field-list simple'}
            )
            pattern = r'Status.\n(?P<status>\w+)'
            status = re.search(pattern, field_list.text).group('status')
            if status not in EXPECTED_STATUS[status_in_column]:
                logging.info(f'\nНесовпадающие статусы:\n{pep_link}'
                             f'\nСтатус в карточке: {status}\n'
                             f'Ожидаемые статусы: '
                             f'{EXPECTED_STATUS[status_in_column]}')
            status_count[status] += 1
    total = 0
    for key, val in status_count.items():
        results.append(
            (key, val)
        )
        total += val
    results.append(('Total', total))
    return results


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)
    if results is not None:
        control_output(results, args)
    logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
