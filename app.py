import requests
from requests_html import HTMLSession
from yaml import load
import os


def read_yaml(filename):
    with open (filename, 'r', encoding='utf8') as f:
        data = load(f)
        f.close()
    return data


def parse_cookie(str):
    cookies = {}
    for line in str.split(';'):
        name, value = line.strip().split('=', 1)
        cookies[name] = value
    return cookies


def get_page_urls(html):
    page_urls_arr = []
    page_urls = html.find('.pagination-wrapper .page-item a')
    for page_url in page_urls:
        # if page_url.attrs['href'].startswith('http://blog.csdn.net/neal1991/article/list'):
        if 'href' in page_url.attrs:
            href = page_url.attrs['href']
            page_urls_arr.append(href)
            print(href)
        page_urls_arr = list(set(page_urls_arr))
    return page_urls_arr


def get_markdown_files(id_list, base_url):
    for id in id_list:
        url = base_url + id
        get_markdown(url)

def get_markdown(url):
    cookies = parse_cookie(config['cookies'])
    r = requests.get(url, cookies=cookies)
    data = r.json()['data']
    title = data['title']
    markdown_content = data['markdowncontent']
    invalid_characaters = '\\/:*?"<>|'
    for c in invalid_characaters:
        title = title.replace(c, '')
    generate_file('data/' + title.strip() + '.md', markdown_content)


def generate_file(filename, content):
    if not os.path.exists(filename):
        if content is None:
            print(filename + 'is none')
        else:
            print(filename)
            with open(filename, 'w', encoding='utf8') as f:
                f.write(content)
                f.close()


def get_article_id_list(url):
    id_list = []
    r = session.get(url)
    html = r.html
    page_urls = get_page_urls(html)
    for page_url in page_urls:
        id_list = id_list + get_article_ids_by_page(page_url)
    # print(id_list)
    return id_list


def get_article_ids_by_page(page_url):
    r = session.get(page_url)
    html = r.html
    article_ids = html.find('.blog-unit a')
    article_isd_arr = []
    for article_id in article_ids:
        href = article_id.attrs['href']
        article_isd_arr.append(parse_article_id(href))
    return article_isd_arr


def parse_article_id(url):
    return url.replace('http://blog.csdn.net/neal1991/article/details/', '')


if __name__ == '__main__':
    config = read_yaml('config.yaml')
    session = HTMLSession()
    id_list = get_article_id_list(config['index_url'])
    get_markdown_files(id_list, config['base_url'])