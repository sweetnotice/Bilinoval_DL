import re
import time
from urllib.parse import urljoin
from src import setting
from src import get_ban_word
from spider_toolbox import requests_tools as requests

base_url = setting.base_url
headers = {
    'authority': 'www.linovelib.com',
    'accept-language': 'zh-CN,zh;q=0.9',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 '
                  'Safari/537.36',
}


def get_noval_id(url: str):
    book_id = url.split('/')[-1].replace('.html', '')
    return book_id


def get_noval_info(noval_id: str) -> dict:
    """
    :param noval_id:
    :return: book_name cover_url description last_update_time last_chapter_name
    """
    url = f'{base_url}/novel/{noval_id}.html'
    resp = requests.get(url, headers)
    resp.raise_for_status()
    resp = resp.text

    book_name = re.search('<h1 class="book-name">(.*?)</h1>', resp).group(1)
    author = re.search('<meta name="author" content="(.*?)" />', resp).group(1)
    cover_url = re.search('book-img fl.*?<img src="(.*?)"', resp, re.S).group(1)
    description = re.search('book-dec Jbook-dec hide.*?<p>(.*?)</p>', resp, re.S).group(1).replace('<br/>', '')
    last_update_time = re.search('<meta property="og:novel:update_time" content="(.*?)" />', resp).group(1)
    last_chapter_name = re.search('<meta property="og:novel:latest_chapter_name" content="(.*?)" />', resp).group(1)

    return {'book_name': book_name,
            'author': author,
            'cover_url': cover_url,
            'description': description,
            'last_update_time': last_update_time,
            'last_chapter_name': last_chapter_name}


def get_noval_chapter(noval_id) -> dict:
    """
    :param noval_id:
    :return: 卷名称part 话名称chapter_name 话链接chapter_url
    """
    url = f'{base_url}/novel/{noval_id}/catalog'
    resp = requests.get(url, headers).text
    items = re.findall('<h2 class="v-line">.*?</ul>', resp, re.S)  # 找到所有卷
    chapter_dict = {'part': [],
                    'chapter_name': [],
                    'chapter_url': []}
    for item in items:  # 单卷解析
        part_name = re.search('<h2 class="v-line">(.*?)</h2>', item).group(1)
        chapter_name_url = re.findall('<li class="col-4"><a href="(.*?)">(.*?)</a></li>', item)
        chapter_url_ = [urljoin(base_url, i[0]) for i in chapter_name_url]
        chapter_url = []
        for i, url_ in enumerate(chapter_url_):
            if 'javascript' in url_:
                # 从上一章获取下一章的链接
                last_url_ = chapter_url_[i - 1]
                resp_ = requests.get(last_url_.replace('.html', '_1000000.html'), headers=headers).text
                url_ = urljoin(last_url_, re.search('书签.*?<a href="(.*?)">下一章</a>', resp_).group(1))
            if url_ not in chapter_url:
                chapter_url.append(url_)
            else:
                raise ''
        chapter_name = [i[1] for i in chapter_name_url]

        chapter_dict['part'].append(part_name)
        chapter_dict['chapter_name'].append(chapter_name)
        chapter_dict['chapter_url'].append(chapter_url)
    return chapter_dict
    # print(item)


def get_chapter_text(chapter_url, debug=None):
    """
    :param chapter_url:
    :return: 整话  整话图片url
    """
    texts = ''
    img_urls = []
    page = 1
    while 1:
        url = chapter_url.replace('.html', f'_{page}.html')
        resp = requests.get(url, headers=headers)
        resp.encoding = 'utf-8'
        resp = resp.text
        text = re.search(
            '<div id="mlfy_main_text">.*?<div id="TextContent" class="read-content">(.*?)(<div class="dag">|</div>)',
            resp, re.S).group(1)
        if not debug:
            text = restore_chars(text)
            texts += text
        else:
            for text_ in re.findall('<p>(.*?)</p>', text):
                texts += text_.replace('\n', '')
        # print(text)
        img_url = re.findall('<img src="(.*?)".*?class="imagecontent">', text)
        for img_url_ in img_url:
            img_urls.append(img_url_)
        page += 1
        time.sleep(0.7)
        if '下一页' not in resp:
            break
        # print(text)
    # print(img_urls)
    # texts = texts.replace('\n', '').replace('<p>', '').replace('<br>', '').replace('</p>', '')
    return texts, img_urls


def get_img_content(url) -> bytes:
    headers = {
        'authority': 'img3.readpai.com',
        'accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
        'accept-language': 'zh-CN,zh;q=0.9',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'referer': 'https://www.linovelib.com/',
        'sec-ch-ua': '"Not A(Brand";v="99", "Google Chrome";v="121", "Chromium";v="121"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'image',
        'sec-fetch-mode': 'no-cors',
        'sec-fetch-site': 'cross-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    }
    resp = requests.get(url, headers=headers).content
    return resp


def restore_chars(text):
    secretMap = get_ban_word.ban_word
    restored_text = ""
    i = 0
    while i < len(text):
        char = text[i]
        if char in secretMap:
            restored_text += secretMap[char]
        else:
            restored_text += char
        i += 1
    return restored_text


if __name__ == '__main__':
    url = 'https://www.linovelib.com/novel/2727.html'
    noval_id = get_noval_id(url)
    # get_noval_chapter(noval_id)
    get_noval_info(noval_id)
    # get_noval_chapter(noval_id)
    a = get_chapter_text('https://www.linovelib.com/novel/2727/150104.html', debug=1)
    # print(get_img_content('https://img3.readpai.com/3/3805/201460/224610.jpg'))
