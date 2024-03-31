import re
import time
from tqdm import tqdm
from urllib.parse import urljoin
import config
from src import get_ban_word
from spider_toolbox import requests_tools as requests

base_url = config.base_url
cookies = {
    'Hm_lvt_ef8d5b3eafdfe7d1bbf72e3f450ad2ed': str(int(time.time())),
    'cf_clearance': 'eIT7XinjwS.PDgrbmimTzE8elvPo1WNGSKuIwOkwga8-1710071101-1.0.1.1-RO2ab4K0rgZEhq93iyCU.GunnUBc77kJ1SBftFY4RIWIyCO9AmPXaPyGNiiwJ5ISEMQR9fYuCodMg.27SuaMUg',
    # 'jieqiRecentRead': '3080.184598.0.1.1710071483.0',
    'Hm_lpvt_ef8d5b3eafdfe7d1bbf72e3f450ad2ed': str(int(time.time())),
}
headers = {
    'authority': 'www.linovelib.com',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'zh-CN,zh;q=0.9',
    'cache-control': 'no-cache',
    'pragma': 'no-cache',
    'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
}


def get_noval_id(url: str):
    book_id = re.search('/novel/(\d+)(.html|/\d+.html)', url).group(1)
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
        chapter_name = []
        now_chapter_url = chapter_url_[0]
        while 1:
            resp_ = requests.get(f'{now_chapter_url.replace(".html", "_100000.html")}', headers=headers).text
            chapter_name_ = re.search('<h1>(.*?)(（|</h1>)', resp_).group(1)
            chapter_name.append(chapter_name_)
            chapter_url.append(now_chapter_url)
            if '下一章' not in resp_:
                break
            now_chapter_url = urljoin(base_url, re.search('书签.*?<a href="(.*?)">下一章</a>', resp_).group(1))
            time.sleep(0.5)

        chapter_dict['part'].append(part_name)
        chapter_dict['chapter_name'].append(chapter_name)
        chapter_dict['chapter_url'].append(chapter_url)
    return chapter_dict
    # print(item)


def while_get_chapter_name_url(start_url: str, end_url: str = False):
    now_url = start_url
    chapter_dict = {'part': [],
                    'chapter_name': [],
                    'chapter_url': []}
    chapter_name = []
    chapter_url = []

    part_name = ''
    while 1:
        resp = requests.get(now_url.replace(".html", "_100000.html"), headers=headers).text
        chapter_name_ = re.search('<h1>(.*?)(（|</h1>)', resp).group(1)
        part_name_ = re.search('<a href="/novel.*?</a> > (.*?)</div>', resp).group(1)

        if part_name != part_name_:
            if part_name != '':  # 为非初始卷的新卷
                chapter_dict['chapter_name'].append(chapter_name)
                chapter_dict['chapter_url'].append(chapter_url)
                chapter_name, chapter_url = [], []
            chapter_dict['part'].append(part_name_)
            part_name = part_name_
            print(f'\n{part_name}')
        chapter_name.append(f'{part_name}-{chapter_name_}')
        print(f'{chapter_name_}')
        chapter_url.append(now_url)
        if '下一章' not in resp:  # 结束
            chapter_dict['chapter_name'].append(chapter_name)
            chapter_dict['chapter_url'].append(chapter_url)
            break
        if now_url != end_url:
            now_url = urljoin(base_url, re.search('书签.*?<a href="(.*?)">下一章</a>', resp).group(1))
            # time.sleep(0.5)
        else:  # 到达指定结束章节(包含)
            chapter_dict['chapter_name'].append(chapter_name)
            chapter_dict['chapter_url'].append(chapter_url)
            break
    return chapter_dict


def get_chapter_text(chapter_url, text_without_format=None):
    """
    :param chapter_url:
    :return: 整话  整话图片url
    :param text_without_format: 输出无格式文本

    """
    texts = ''
    img_urls = []
    page = 1
    while 1:
        url = chapter_url.replace('.html', f'_{page}.html')
        resp = requests.get(url, headers=headers, cookies=cookies)
        resp.encoding = 'utf-8'
        resp = resp.text
        text = re.search(
            '<div id="mlfy_main_text">.*?<div id="TextContent" class="read-content">(.*?)(<div class="dag">|</div>)',
            resp, re.S).group(1)
        if '内容加载失败' in text:
            print('内容加载失败')
            raise '内容加载失败'
        if not text_without_format:
            text = restore_chars(text)
            texts += text
        else:
            for text_ in re.findall('<p>(.*?)</p>', text):
                texts += text_.replace('\n', '')
        # print(text)
        img_url = re.findall('<img[^>]+(src|data-src)="(.*?\.(jpg|png))" (class="imagecontent|style)', text)
        for img_url_ in img_url:
            img_urls.append(img_url_[1])
        page += 1
        time.sleep(0.7)
        if '下一页' not in resp:
            break
        # print(text)
    # print(img_urls)
    # texts = texts.replace('\n', '').replace('<p>', '').replace('<br>', '').replace('</p>', '')
    return texts, img_urls


def get_img_content(url) -> bytes:
    headers_ = {
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
    resp = requests.get(url, headers=headers_, info=True).content
    return resp


def restore_chars(text):
    ban_word = get_ban_word.ban_word
    restored_text = ""
    i = 0
    while i < len(text):
        char = text[i]
        if char in ban_word:
            restored_text += ban_word[char]
        else:
            restored_text += char
        i += 1
    return restored_text


if __name__ == '__main__':
    # url = 'https://www.linovelib.com/novel/3048.html'
    # noval_id = get_noval_id(url)
    # get_noval_chapter(noval_id)
    # get_noval_info(noval_id)
    # get_noval_chapter(noval_id)
    a = get_chapter_text('https://www.linovelib.com/novel/111/116403.html', text_without_format=1)
    # print(get_img_content('https://img3.readpai.com/3/3805/201460/224610.jpg'))
    # get_noval_part_chapter_name('3080')
    # while_get_chapter_name_url('https://www.linovelib.com/novel/3080/197281.html',
    #                            'https://www.linovelib.com/novel/3080/226845.html')
    get_img_content('https://img3.readpai.com/0/111/116397/189148.jpg')
